from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Header, Form
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.rate_limit import rate_limit 
from ..models.vpn import VPNConfig, Organization
from ..services.vpn_manager import vpn_manager
from ..services.secrets_manager import SecretsManager
from typing import Dict
import logging
import jwt
import uuid
import os
import aiofiles
import json

logger = logging.getLogger(__name__)
router = APIRouter()
secrets_manager = SecretsManager()

def get_token_data(authorization: str = Header(None)):
    """Extract data from JWT token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Remove 'Bearer ' prefix
        token = authorization.replace('Bearer ', '')
        # Decode token without verification (as it's already verified by auth service)
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/config", status_code=201)
async def upload_vpn_config(
    file: UploadFile = File(...),
    username: str = Form(...),
    password: str = Form(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Upload VPN configuration file with authentication credentials."""
    try:
        # Verify token and get user data
        token_data = get_token_data(authorization)
        org_id = token_data.get('org_id')
        user_email = token_data.get('sub')  # Changed from 'email' to 'sub' as that's what's in your token
        
        if not user_email:
            raise HTTPException(
                status_code=400,
                detail="User email not found in token"
            )
        
        # Get organization
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(
                status_code=404,
                detail="Organization not found"
            )
        
        # Create VPN config entry
        vpn_config = VPNConfig(
            organization_id=org_id,
            user_email=user_email,  # This was missing before
            name=file.filename,
            config_metadata={
                "original_filename": file.filename,
                "content_type": file.content_type,
                "size": len(await file.read())
            }
        )
        
        db.add(vpn_config)
        db.commit()
        db.refresh(vpn_config)
        
        # Read the config file content
        await file.seek(0)  # Reset file pointer to beginning
        config_content = await file.read()
        
        # Store in AWS
        aws_result = await secrets_manager.store_vpn_config(
            str(vpn_config.config_id),
            config_content.decode(),
            {"username": username, "password": password}
        )
        
        # Update organization VPN status
        org.vpn_configured = True
        db.commit()
        
        logger.info(f"VPN config uploaded successfully. Config ID: {vpn_config.config_id}")
        
        return {
            "message": "VPN configuration uploaded successfully",
            "config_id": str(vpn_config.config_id),
            "name": vpn_config.name,
            "status": vpn_config.status,
            "organization_id": org_id,
            "aws": aws_result
        }
        
    except Exception as e:
        logger.error(f"Error uploading VPN config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading VPN config: {str(e)}"
        )

@router.post("/connect/{config_id}", status_code=200)
async def connect_vpn(
    config_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Connect to VPN using specified configuration."""
    try:
        # Verify token and get user data
        token_data = get_token_data(authorization)
        org_id = token_data.get('org_id')
        
        # Get VPN config
        config = db.query(VPNConfig).filter(
            VPNConfig.config_id == config_id,
            VPNConfig.organization_id == org_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="VPN configuration not found"
            )
        
        # Get config and credentials from AWS
        vpn_data = await secrets_manager.get_vpn_config(str(config.config_id))
        
        # Create temporary config file
        config_path = os.path.join(vpn_manager.vpn_config_dir, f"{config.config_id}.ovpn")
        async with aiofiles.open(config_path, 'w') as f:
            await f.write(vpn_data["config"])
            await f.write(f"\nauth-user-pass /etc/openvpn/auth/{config.config_id}.txt\n")
        
        # Create auth file
        auth_dir = "/etc/openvpn/auth"
        os.makedirs(auth_dir, exist_ok=True)
        auth_path = os.path.join(auth_dir, f"{config.config_id}.txt")
        async with aiofiles.open(auth_path, 'w') as f:
            await f.write(f"{vpn_data['credentials']['username']}\n{vpn_data['credentials']['password']}\n")
        
        # Set proper permissions
        os.chmod(config_path, 0o600)
        os.chmod(auth_path, 0o600)
        
        # Connect to VPN
        result = await vpn_manager.connect(config, db)
        return result
        
    except Exception as e:
        logger.error(f"Error connecting to VPN: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to VPN: {str(e)}"
        )
    
@router.delete("/config/{config_id}", status_code=200)
async def delete_vpn_config(
    config_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Delete VPN configuration and credentials."""
    try:
        # Verify token and get user data
        token_data = get_token_data(authorization)
        org_id = token_data.get('org_id')
        
        # Get VPN config
        config = db.query(VPNConfig).filter(
            VPNConfig.config_id == config_id,
            VPNConfig.organization_id == org_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="VPN configuration not found"
            )
        
        # Delete from AWS
        await secrets_manager.delete_vpn_config(str(config.config_id))
        
        # Delete from database
        db.delete(config)
        db.commit()
        
        return {
            "message": "VPN configuration deleted successfully",
            "config_id": str(config.config_id)
        }
        
    except Exception as e:
        logger.error(f"Error deleting VPN config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting VPN config: {str(e)}"
        )
    
@router.post("/disconnect/{config_id}", status_code=200)
async def disconnect_vpn(
    config_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Disconnect from VPN."""
    try:
        # Verify token and get user data
        token_data = get_token_data(authorization)
        org_id = token_data.get('org_id')
        
        # Get VPN config
        config = db.query(VPNConfig).filter(
            VPNConfig.config_id == config_id,
            VPNConfig.organization_id == org_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="VPN configuration not found"
            )
        
        # Disconnect from VPN
        result = await vpn_manager.disconnect(config, db)
        return result
        
    except Exception as e:
        logger.error(f"Error disconnecting from VPN: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error disconnecting from VPN: {str(e)}"
        )

@router.get("/status/{config_id}", status_code=200)
async def get_vpn_status(
    config_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get VPN connection status."""
    try:
        # Verify token and get user data
        token_data = get_token_data(authorization)
        org_id = token_data.get('org_id')
        
        logger.info(f"Checking VPN status for config_id: {config_id}, org_id: {org_id}")
        
        # Query using the correct column name from the database
        config = db.query(VPNConfig).filter(
            VPNConfig.config_id == config_id,  # This should match the column name in the DB
            VPNConfig.organization_id == org_id,
            VPNConfig.is_active == True  # Add this to ensure we only get active configs
        ).first()
        
        if not config:
            # Log the actual query for debugging
            logger.error(f"VPN config not found. Params: config_id={config_id}, org_id={org_id}")
            # Try to find any config with this ID to give better error messages
            any_config = db.query(VPNConfig).filter(
                VPNConfig.config_id == config_id
            ).first()
            
            if any_config:
                logger.error(f"Config exists but with org_id={any_config.organization_id}")
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to access this VPN configuration"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail="VPN configuration not found"
                )
        
        # Get status
        result = await vpn_manager.get_status(config)
        logger.info(f"VPN status result: {result}")
        
        # Return status with additional metadata
        return {
            "status": config.status,
            "config_id": str(config.config_id),
            "organization_id": config.organization_id,
            "connection_type": config.connection_type,
            "tunnel_info": result.get("tunnel_info") if isinstance(result, dict) else None,
            "last_used_at": config.last_used_at.isoformat() if config.last_used_at else None
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting VPN status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting VPN status: {str(e)}"
        )

@router.get("/interface/{config_id}", status_code=200)
async def get_vpn_interface(
    config_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get VPN interface information."""
    try:
        # Verify token and get user data
        token_data = get_token_data(authorization)
        org_id = token_data.get('org_id')
        
        logger.info(f"Getting VPN interface info for config_id: {config_id}, org_id: {org_id}")
        
        # Get VPN config
        config = db.query(VPNConfig).filter(
            VPNConfig.config_id == config_id,
            VPNConfig.organization_id == org_id,
            VPNConfig.is_active == True
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="VPN configuration not found"
            )
        
        # Get interface info from VPN manager
        interface_info = await vpn_manager.get_interface_info(config)
        
        return {
            "config_id": str(config.config_id),
            "interface": interface_info.get("interface"),
            "local_ip": interface_info.get("local_ip"),
            "netmask": interface_info.get("netmask"),
            "routes": interface_info.get("routes", []),
            "status": config.status
        }
        
    except Exception as e:
        logger.error(f"Error getting VPN interface info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting VPN interface info: {str(e)}"
        )
    
@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """Get VPN service metrics."""
    try:
        active_connections = db.query(VPNConfig).filter(VPNConfig.status == 'connected').count()
        total_configs = db.query(VPNConfig).count()
        return {
            "active_connections": active_connections,
            "total_configs": total_configs,
            "uptime": "healthy",
            "memory_usage": psutil.Process().memory_info().rss / 1024 / 1024  # MB
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")
    
@router.get("/debug/enums")
async def debug_enums():
    """Debug endpoint to verify enum values."""
    return {
        "status_type": str(vpn_status_type),
        "connection_type": str(vpn_connection_type)
    }

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid
from ..core.database import Base

# Create custom enum types
vpn_status_type = ENUM(
    'configured',
    'connecting',
    'connected',
    'disconnected',
    'error',
    name='vpnstatustype',
    schema='public',
    create_type=False
)

vpn_connection_type = ENUM(
    'openvpn',
    'ssh',
    'fortinet_ssl',
    name='vpnconnectiontype',
    schema='public',
    create_type=False
)

class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    vpn_configured = Column(Boolean, default=False)
    vpn_gateway_config = Column(JSONB, nullable=True)

class VPNConfig(Base):
    __tablename__ = "vpn_configurations"
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True)
    config_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    organization_id = Column(Integer, ForeignKey('public.organizations.id', ondelete='CASCADE'), nullable=False)
    user_email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True))
    status = Column(vpn_status_type, server_default=text("'configured'::vpnstatustype"))
    connection_type = Column(vpn_connection_type, server_default=text("'openvpn'::vpnconnectiontype"))
    config_metadata = Column(JSONB, default={})
    secret_arn = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    organization = relationship("Organization", backref="vpn_configs")

    def __repr__(self):
        return f"<VPNConfig(config_id={self.config_id}, name={self.name})>"
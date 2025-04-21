from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VPNConfigBase(BaseModel):
    config_name: str
    user_id: str

class VPNConfigCreate(VPNConfigBase):
    pass

class VPNConfigRequest(BaseModel):
    username: str
    password: str
    config_name: str
    
class VPNConfigResponse(VPNConfigBase):
    config_id: str
    created_at: datetime
    status: str
    
    class Config:
        from_attributes = True

class VPNConnectionStatus(BaseModel):
    config_id: str
    status: str
    started_at: Optional[datetime]
    error_message: Optional[str] = None

class VPNCredentials(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    certificate: Optional[str] = None
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "VPN Connector Service"
    API_V1_STR: str = "/api/v1"
    
    # AWS Settings
    AWS_REGION: str
    AWS_ACCOUNT_ID: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_SECRET_PREFIX: str = "/vpn/configs/vpn/" 
    
    # VPN Settings
    VPN_CONFIG_PATH: str = "/etc/openvpn/configs"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
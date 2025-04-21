import boto3
import json
from botocore.exceptions import ClientError
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class SecretsManager:
    def __init__(self):
        self.secrets_client = boto3.client(
            'secretsmanager',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.secrets_prefix = "/vpn/configs/vpn/"
        self.s3_bucket = "043309327369-vpn-config"

    async def store_vpn_config(self, config_id: str, config_data: str, credentials: dict) -> str:
        """Store VPN configuration and credentials in AWS."""
        try:
            # Store credentials in Secrets Manager
            secret_name = f"{self.secrets_prefix}{config_id}"
            secret_value = {
                "username": credentials.get("username"),
                "password": credentials.get("password")
            }

            try:
                self.secrets_client.create_secret(
                    Name=secret_name,
                    SecretString=json.dumps(secret_value)
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceExistsException':
                    self.secrets_client.update_secret(
                        SecretId=secret_name,
                        SecretString=json.dumps(secret_value)
                    )
                else:
                    raise

            # Store config file in S3
            s3_key = f"configs/{config_id}.ovpn"
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=config_data.encode(),
                ServerSideEncryption='AES256'
            )

            return {
                "secret_arn": f"arn:aws:secretsmanager:{settings.AWS_REGION}:{settings.AWS_ACCOUNT_ID}:secret:{secret_name}",
                "s3_key": s3_key
            }

        except Exception as e:
            logger.error(f"Error storing VPN configuration: {str(e)}")
            raise

    async def get_vpn_config(self, config_id: str) -> dict:
        """Retrieve VPN configuration and credentials from AWS."""
        try:
            # Get credentials from Secrets Manager using full ARN
            secret_id = f"{self.secrets_prefix}{config_id}"
            try:
                logger.info(f"Attempting to get secret: {secret_id}")
                secret_response = self.secrets_client.get_secret_value(
                    SecretId=secret_id
                )
            except ClientError as e:
                # If not found, try with the -R5x3dt suffix
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    secret_id_with_suffix = f"{secret_id}-R5x3dt"
                    logger.info(f"Retrying with suffix: {secret_id_with_suffix}")
                    secret_response = self.secrets_client.get_secret_value(
                        SecretId=secret_id_with_suffix
                    )
                else:
                    raise

            credentials = json.loads(secret_response['SecretString'])

            # Get config file from S3
            s3_key = f"configs/{config_id}.ovpn"
            s3_response = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            config_data = s3_response['Body'].read().decode()

            return {
                "config": config_data,
                "credentials": credentials
            }

        except Exception as e:
            logger.error(f"Error retrieving VPN configuration: {str(e)}")
            raise

    async def delete_vpn_config(self, config_id: str) -> None:
        """Delete VPN configuration and credentials from AWS."""
        try:
            # Delete from Secrets Manager
            secret_name = f"{self.secrets_prefix}{config_id}"
            self.secrets_client.delete_secret(
                SecretId=secret_name,
                ForceDeleteWithoutRecovery=True
            )

            # Delete from S3
            s3_key = f"configs/{config_id}.ovpn"
            self.s3_client.delete_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )

        except Exception as e:
            logger.error(f"Error deleting VPN configuration: {str(e)}")
            raise
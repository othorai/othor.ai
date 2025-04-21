from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import os
import urllib.parse

logger = logging.getLogger(__name__)

def create_database_url():
    """Create database URL with properly encoded credentials."""
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    sslmode = os.getenv('DB_SSLMODE')
    
    # Encode the password to handle special characters
    encoded_password = urllib.parse.quote_plus(password)
    encoded_user = urllib.parse.quote_plus(user)
    
    logger.info(f"Connecting to database at {host}:{port}/{db_name} as {user}")
    
    return (
        f"postgresql://{encoded_user}:{encoded_password}"
        f"@{host}:{port}/{db_name}?sslmode={sslmode}"
    )

# Create MetaData instance
metadata = MetaData(schema='public')

# Create Base class with the correct schema
Base = declarative_base(metadata=metadata)

try:
    database_url = create_database_url()
    
    # Create SQLAlchemy engine with connection pooling settings
    engine = create_engine(
        database_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=False
    )
    
    # Test the connection and check if organizations table exists
    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT 1 FROM organizations LIMIT 1"))
            logger.info("Successfully connected to database and verified organizations table")
        except Exception as e:
            logger.error(f"Organizations table check failed: {str(e)}")
            raise

except Exception as e:
    logger.error(f"Database connection error: {str(e)}")
    raise

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
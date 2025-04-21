from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VPN Connector Service",
    description="Service for managing VPN connections",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="", tags=["vpn"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting VPN Connector Service")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down VPN Connector Service")
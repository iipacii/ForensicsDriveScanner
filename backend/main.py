# main.py
from fastapi import FastAPI, Request
from app.api.routes import router
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
import sys

import os
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Use absolute path for log file
log_file = log_dir / "api.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(log_file), mode='a', encoding='utf-8')
    ],
    force=True  # Force reconfiguration of the root logger
)

# Create a named logger for your application
logger = logging.getLogger("api")
logger.info("Logger initialized - testing logging configuration")

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Incoming request - Method: {request.method} Path: {request.url.path}")
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        logger.info(
            f"Request completed - Method: {request.method} Path: {request.url.path} "
            f"Status: {response.status_code} Duration: {duration:.2f}s"
        )
        return response
    except Exception as e:
        logger.error(f"Request failed - Error: {str(e)}")
        raise

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router without additional prefix since routes.py already has /drives
app.include_router(router)

# Optional: Add root route for testing
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "API Running"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any
from datetime import datetime
import asyncio
import json
import os
import logging
from resume_builder import intake_job_post, JobPost
from data import router as data_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume Builder API",
    description="API for managing skills, core competencies, and accomplishments",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the data router
app.include_router(data_router)

def save_job_post(job_post: JobPost) -> str:
    """
    Save the job post as a JSON file.
    Returns the filename that was used.
    """
    logger.info("Starting to save job post")
    try:
        # Create data directory if it doesn't exist
        data_dir = "data/job_posts"
        os.makedirs(data_dir, exist_ok=True)
        
        # Create filename using timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_dir}/job_post_{timestamp}.json"
        
        # Convert job post to dict, handling datetime serialization
        job_post_dict = {
            "html": job_post.html,
            "url": str(job_post.url),
            "timestamp": job_post.timestamp.isoformat()
        }
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(job_post_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Job post saved successfully to: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving job post: {str(e)}", exc_info=True)
        raise

@app.post("/job_post")
async def create_job_post(job_post: JobPost):
    logger.info("Received new job post request")
    try:
        # Save the job post
        # try:
        #     filename = save_job_post(job_post)
        #     logger.info(f"Job post saved to: {filename}")
        # except Exception as e:
        #     logger.error(f"Error saving job post: {str(e)}", exc_info=True)
        
        # Start background processing
        logger.info("Starting background processing of job post")
        asyncio.create_task(intake_job_post(job_post))
        
        response = {
            "message": "Job post received and processing started",
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info("Job post request processed successfully")
        return response
    except Exception as e:
        error_msg = f"Error processing job post request: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise


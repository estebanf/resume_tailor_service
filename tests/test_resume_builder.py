import pytest
import json
import os
import logging
from datetime import datetime
from resume_builder import JobPost, process_job_post

# Configure logging for tests
@pytest.fixture(autouse=True)
def setup_logging():
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True  # This overwrites any existing configuration
    )
    yield

def load_job_post_from_file(filename: str) -> JobPost:
    """Helper function to load a job post from a JSON file."""
    logging.info(f"Loading job post from file: {filename}")
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return JobPost(
            html=data['html'],
            url=data['url'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )

@pytest.mark.asyncio
async def test_job_post_fit():
    """Test processing a job post that should be a good fit."""
    logging.info("Starting test_job_post_fit")
    
    # Load the job post from file
    job_post = load_job_post_from_file('data/job_posts/job_post_fit.json')
    
    try:
        # Process the job post
        await process_job_post(job_post)
        logging.info("test_job_post_fit completed successfully")
        assert True
    except Exception as e:
        logging.error(f"test_job_post_fit failed: {str(e)}", exc_info=True)
        pytest.fail(f"Processing fit job post failed: {str(e)}")

@pytest.mark.asyncio
async def test_job_post_unfit():
    """Test processing a job post that should not be a fit."""
    logging.info("Starting test_job_post_unfit")
    
    # Load the job post from file
    job_post = load_job_post_from_file('data/job_posts/job_post_unfit.json')
    
    try:
        # Process the job post
        await process_job_post(job_post)
        logging.info("test_job_post_unfit completed successfully")
        assert True
    except Exception as e:
        logging.error(f"test_job_post_unfit failed: {str(e)}", exc_info=True)
        pytest.fail(f"Processing unfit job post failed: {str(e)}")

# @pytest.mark.asyncio
# async def test_process_job_post():
#     # Create a sample job post
#     job_post = JobPost(
#         html="<div>Test job description</div><div>Insights about this job's applicants</div><div>Should be removed</div>",
#         url="https://www.linkedin.com/jobs/collections/recommended/?currentJobId=123456&discover=recommended",
#         timestamp=datetime.utcnow()
#     )
    
#     # Process the job post
#     # Since the function returns None, we're testing that it executes without errors
#     try:
#         await process_job_post(job_post)
#         assert True  # If we get here, the function executed without errors
#     except Exception as e:
#         pytest.fail(f"process_job_post raised an exception: {str(e)}")

# @pytest.mark.asyncio
# async def test_process_job_post_with_invalid_url():
#     # Test with an invalid URL
#     job_post = JobPost(
#         html="<div>Test job description</div>",
#         url="https://www.linkedin.com/jobs/view/invalid",  # URL without job ID
#         timestamp=datetime.utcnow()
#     )
    
#     # The function should handle invalid URLs gracefully
#     try:
#         await process_job_post(job_post)
#         assert True
#     except Exception as e:
#         pytest.fail(f"process_job_post failed with invalid URL: {str(e)}")

# @pytest.mark.asyncio
# async def test_process_job_post_with_empty_html():
#     # Test with empty HTML
#     job_post = JobPost(
#         html="",
#         url="https://www.linkedin.com/jobs/collections/recommended/?currentJobId=123456",
#         timestamp=datetime.utcnow()
#     )
    
#     # The function should handle empty HTML gracefully
#     try:
#         await process_job_post(job_post)
#         assert True
#     except Exception as e:
#         pytest.fail(f"process_job_post failed with empty HTML: {str(e)}") 
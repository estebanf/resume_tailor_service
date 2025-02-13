from typing import List
from openai import OpenAI
import logging

# Configure logging
logger = logging.getLogger(__name__)

def get_embeddings(text: str) -> List[float]:
    """
    Get embeddings for a text using OpenAI's API.
    
    Args:
        text: The text to get embeddings for
        
    Returns:
        List[float]: The embedding vector
    """
    try:
        logger.debug(f"Getting embeddings for text: {text[:100]}...")
        openai_client = OpenAI()
        response = openai_client.embeddings.create(input=text, model="text-embedding-3-large")
        logger.debug("Successfully retrieved embeddings")
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error getting embeddings: {str(e)}", exc_info=True)
        raise 
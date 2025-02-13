import pytest
import json
import os
import logging
from models import Analysis
from accomplishments import (
    get_accomplishments, 
    retrieve_accomplishment_by_skill, 
    retrieve_accomplishment_by_core_competency,
    retrieve_accomplishment_by_experience,
    COMPANIES
)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # This ensures our configuration takes precedence
)

# Configure test logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure all child loggers also show INFO
logging.getLogger('accomplishments').setLevel(logging.INFO)

def load_analysis_from_file(filename: str = 'inputs/02_analysis_result.json') -> Analysis:
    """Helper function to load analysis from a JSON file."""
    logger.info(f"Loading analysis from {filename}")
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return Analysis(**data)

def verify_accomplishment_structure(accomplishment: dict):
    """Helper function to verify the structure of an accomplishment."""
    assert "id" in accomplishment
    assert "title" in accomplishment
    assert "body" in accomplishment
    assert "similarity" in accomplishment
    assert "skills" in accomplishment
    assert "core_competencies" in accomplishment
    
    # Verify data types
    assert isinstance(accomplishment["id"], int)
    assert isinstance(accomplishment["title"], str)
    assert isinstance(accomplishment["body"], str)
    assert isinstance(accomplishment["similarity"], float)
    assert isinstance(accomplishment["skills"], list)
    assert isinstance(accomplishment["core_competencies"], list)
    
    # # Verify similarity is within expected range
    # assert 0.5 <= accomplishment["similarity"] <= 1.0

def verify_results_structure(results: dict):
    """Helper function to verify the structure of results dictionary."""
    assert isinstance(results, dict)
    for company in COMPANIES:
        assert company in results
        assert isinstance(results[company], list)
        
        # If there are results for this company
        for accomplishment in results[company]:
            verify_accomplishment_structure(accomplishment)
            
        # Verify results are sorted by similarity
        if len(results[company]) > 1:
            for i in range(len(results[company]) - 1):
                assert results[company][i]["similarity"] >= results[company][i + 1]["similarity"]

def verify_analysis_scores_structure(scores: dict):
    """Helper function to verify the structure of analysis scores."""
    assert isinstance(scores, dict)
    assert "skills" in scores
    assert "core_competencies" in scores
    assert "experiences" in scores
    
    # Verify each category
    for category in ["skills", "core_competencies", "experiences"]:
        assert isinstance(scores[category], list)
        for item in scores[category]:
            assert isinstance(item, dict)
            assert "name" in item
            assert "score" in item
            assert isinstance(item["name"], str)
            assert isinstance(item["score"], float)
            assert item["score"] >= 0.0  # Scores should be non-negative

@pytest.mark.asyncio
async def test_get_accomplishments():
    """Test retrieving accomplishments based on job analysis."""
    logger.info("Starting test_get_accomplishments")
    # Load the analysis from file
    analysis = load_analysis_from_file()
    os.environ["JOB_RUN"] = f'{analysis.company_name} - {analysis.job_title}'
    
    # Verify the analysis was loaded correctly
    assert analysis.company_name == "DigitalOcean"
    assert analysis.job_title == "Director, Product Management (AI/ML)"
    assert len(analysis.core_competencies) > 0
    assert len(analysis.skills_required) > 0
    assert len(analysis.expected_experiences) > 0
    
    # Get accomplishments
    results, scores = await get_accomplishments(analysis)
    
    # Verify the structure of both results and scores
    verify_results_structure(results)
    verify_analysis_scores_structure(scores)
    
    # Verify scores were calculated for all items
    assert len(scores["skills"]) == len(analysis.skills_required)
    assert len(scores["core_competencies"]) == len(analysis.core_competencies)
    assert len(scores["experiences"]) == len(analysis.expected_experiences)
    logger.info("Completed test_get_accomplishments")

@pytest.mark.asyncio
async def test_retrieve_accomplishment_by_skill():
    """Test retrieving accomplishments for a specific skill."""
    logger.info("Starting test_retrieve_accomplishment_by_skill")
    # Initialize results dictionary
    results = {company: [] for company in COMPANIES}
    
    # Initialize analysis for scores
    analysis = load_analysis_from_file()
    scores = {
        "skills": [{"name": "AI/ML", "score": 0.0}],
        "core_competencies": [],
        "experiences": []
    }
    
    # Test with an AI-related skill since we know we have that in the sample data
    skill = "AI/ML"
    
    # Get accomplishments for the skill
    await retrieve_accomplishment_by_skill(results, skill, scores)
    
    # Verify the structures
    verify_results_structure(results)
    verify_analysis_scores_structure(scores)
    
    # Verify the skill score was updated
    assert scores["skills"][0]["name"] == "AI/ML"
    assert scores["skills"][0]["score"] > 0.0
    logger.info("Completed test_retrieve_accomplishment_by_skill")

@pytest.mark.asyncio
async def test_retrieve_accomplishment_by_core_competency():
    """Test retrieving accomplishments for a core competency."""
    logger.info("Starting test_retrieve_accomplishment_by_core_competency")
    # Initialize results dictionary
    results = {company: [] for company in COMPANIES}
    
    # Initialize analysis for scores
    scores = {
        "skills": [],
        "core_competencies": [{"name": "Leadership", "score": 0.0}],
        "experiences": []
    }
    
    # Test with a leadership competency since we know we have that in the sample data
    competency = "Leadership"
    
    # Get accomplishments for the competency
    await retrieve_accomplishment_by_core_competency(results, competency, scores)
    
    # Verify the structures
    verify_results_structure(results)
    verify_analysis_scores_structure(scores)
    
    # Verify the competency score was updated
    assert scores["core_competencies"][0]["name"] == "Leadership"
    assert scores["core_competencies"][0]["score"] > 0.0
    logger.info("Completed test_retrieve_accomplishment_by_core_competency")

@pytest.mark.asyncio
async def test_retrieve_accomplishment_by_experience():
    """Test retrieving accomplishments for an experience requirement."""
    logger.info("Starting test_retrieve_accomplishment_by_experience")
    # Initialize results dictionary
    results = {company: [] for company in COMPANIES}
    
    # Initialize analysis for scores
    scores = {
        "skills": [],
        "core_competencies": [],
        "experiences": [{"name": "Experience with AI/ML product portfolios", "score": 0.0}]
    }
    
    # Test with an experience requirement from the sample data
    experience = "Experience with AI/ML product portfolios"
    
    # Get accomplishments for the experience
    await retrieve_accomplishment_by_experience(results, experience, scores)
    
    # Verify the structures
    verify_results_structure(results)
    verify_analysis_scores_structure(scores)
    
    # Verify the experience score was updated
    assert scores["experiences"][0]["name"] == "Experience with AI/ML product portfolios"
    assert scores["experiences"][0]["score"] > 0.0
    logger.info("Completed test_retrieve_accomplishment_by_experience") 
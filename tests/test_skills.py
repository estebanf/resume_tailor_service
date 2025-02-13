import pytest
import json
import os
from models import Analysis
from skills import get_skills, TOP_N
import logging

# Configure logging
logger = logging.getLogger(__name__)

def load_analysis_from_file(filename: str = 'inputs/02_analysis_result.json') -> Analysis:
    """Helper function to load analysis from a JSON file."""
    logger.info(f"Loading analysis from {filename}")
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return Analysis(**data)

def load_accomplishments_from_file(filename: str = 'inputs/03_accomplishments.json') -> dict:
    """Helper function to load accomplishments from a JSON file."""
    logger.info(f"Loading accomplishments from {filename}")
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data["accomplishments"]

def verify_skills_summary_structure(summary: dict):
    """Helper function to verify the structure of the skills summary."""
    assert isinstance(summary, dict)
    assert "top_skills" in summary
    assert "top_competencies" in summary
    
    # Verify top skills
    assert isinstance(summary["top_skills"], list)
    assert len(summary["top_skills"]) <= TOP_N
    for skill in summary["top_skills"]:
        assert isinstance(skill, dict)
        assert "id" in skill
        assert "name" in skill
        assert "similarity" in skill
        assert isinstance(skill["id"], int)
        assert isinstance(skill["name"], str)
        assert isinstance(skill["similarity"], float)
        assert 0 <= skill["similarity"] <= 1
    
    # Verify top competencies
    assert isinstance(summary["top_competencies"], list)
    assert len(summary["top_competencies"]) <= TOP_N
    for comp in summary["top_competencies"]:
        assert isinstance(comp, dict)
        assert "id" in comp
        assert "name" in comp
        assert "similarity" in comp
        assert isinstance(comp["id"], int)
        assert isinstance(comp["name"], str)
        assert isinstance(comp["similarity"], float)
        assert 0 <= comp["similarity"] <= 1
    
    # Verify sorting
    if summary["top_skills"]:
        for i in range(len(summary["top_skills"]) - 1):
            assert summary["top_skills"][i]["similarity"] >= summary["top_skills"][i + 1]["similarity"]
    
    if summary["top_competencies"]:
        for i in range(len(summary["top_competencies"]) - 1):
            assert summary["top_competencies"][i]["similarity"] >= summary["top_competencies"][i + 1]["similarity"]

@pytest.mark.asyncio
async def test_get_skills():
    """Test the get_skills function using input files."""
    logger.info("Starting test_get_skills")
    
    # Load test data
    analysis = load_analysis_from_file()
    accomplishments = load_accomplishments_from_file()
    
    # Get skills summary
    skills_summary = await get_skills(analysis, accomplishments)
    
    # Verify the structure and content
    verify_skills_summary_structure(skills_summary)
    
    # Verify file was created
    assert os.path.exists('inputs/04_skills.json')
    
    # Load and verify saved file
    with open('inputs/04_skills.json', 'r', encoding='utf-8') as f:
        saved_summary = json.load(f)
        verify_skills_summary_structure(saved_summary)
        assert saved_summary == skills_summary
    
    logger.info("Completed test_get_skills") 
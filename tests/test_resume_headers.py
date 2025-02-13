import json
import pytest
from models import Analysis, TopSkills, ProfessionalSummary, Skill
from resume_headers import get_key_skills, get_professional_summary

def load_json_file(filename: str) -> dict:
    """Helper function to load JSON files from inputs directory."""
    with open(f'inputs/{filename}', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_text_file(filename: str) -> str:
    """Helper function to load text files from inputs directory."""
    with open(f'inputs/{filename}', 'r', encoding='utf-8') as f:
        return f.read()

def verify_skills_structure(skills: TopSkills):
    """Helper function to verify the structure of generated skills."""
    assert isinstance(skills, TopSkills)
    assert len(skills.skills) > 0
    for skill in skills.skills:
        assert isinstance(skill, Skill)
        assert len(skill.skill.split()) <= 3
        assert skill.candidate_skill_or_core_competency

def verify_summary_structure(summary: ProfessionalSummary):
    """Helper function to verify the structure of generated summary."""
    assert isinstance(summary, ProfessionalSummary)
    assert summary.summary
    assert len(summary.summary) > 0
    assert len(summary.summary.split()) >= 50  # Ensure it's a substantial summary

@pytest.mark.asyncio
async def test_get_key_skills():
    """Test the get_key_skills function using input files."""
    # Load required input files
    analysis_data = load_json_file('02_analysis_result.json')
    accomplishments_data = load_json_file('03_accomplishments.json')
    skills_data = load_json_file('04_skills.json')
    
    # Create Analysis object
    analysis = Analysis(**analysis_data)
    
    # Call get_key_skills
    result = await get_key_skills(analysis, skills_data)
    
    # Verify the result
    verify_skills_structure(result)
    
    # Additional checks
    assert len(result.skills) == 12  # Should generate exactly 10 skills
    
    # Check if skills reference actual candidate skills/competencies
    all_candidate_skills = set(
        [skill["name"] for skill in skills_data["top_skills"]] +
        [comp["name"] for comp in skills_data["top_competencies"]]
    )
    
    for skill in result.skills:
        assert skill.candidate_skill_or_core_competency in all_candidate_skills

    # write the result to a file
    with open('inputs/05_key_skills.json', 'w', encoding='utf-8') as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

@pytest.mark.asyncio
async def test_get_professional_summary():
    """Test the get_professional_summary function using input files."""
    # Load required input files
    job_post = load_text_file('01_job_post.txt')
    analysis_data = load_json_file('02_analysis_result.json')
    accomplishments_data = load_json_file('03_accomplishments.json')
    key_skills_data = load_json_file('05_key_skills.json')
    
    # Create required objects
    analysis = Analysis(**analysis_data)
    key_skills = TopSkills(**key_skills_data)
    
    # Call get_professional_summary
    result = await get_professional_summary(
        job_post,
        accomplishments_data["accomplishments"],
        key_skills,
        analysis
    )
    
    # Verify the result
    verify_summary_structure(result)
    
    # Additional checks
    # summary_lower = result.summary.lower()
    
    # Check if summary mentions job title
    # assert analysis.job_title.lower() in summary_lower
    
    # Check if summary mentions at least one key skill
    # assert any(skill.skill.lower() in summary_lower for skill in key_skills.skills)
    
    # Check if summary mentions company name
    # assert analysis.company_name.lower() in summary_lower 

    # write the result to a file
    with open('inputs/06_professional_summary.json', 'w', encoding='utf-8') as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

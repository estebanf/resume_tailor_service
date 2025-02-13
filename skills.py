from typing import Dict, List, Any, Tuple
from models import Analysis
import logging
import json
import os
from embeddings import get_embeddings
from neo4j import GraphDatabase
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# Constants
URI = "bolt://localhost:7687"
AUTH = ("", "")
TOP_N = 15

def calculate_cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calculate cosine similarity between two embeddings."""
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

def get_skill_embedding(driver: GraphDatabase.driver, skill_name: str) -> Tuple[int, List[float]]:
    """
    Get embedding for a skill from the database.
    
    Args:
        driver: Neo4j driver
        skill_name: Name of the skill
        
    Returns:
        Tuple containing skill ID and embedding
    """
    with driver.session() as session:
        query = """
        MATCH (s:Skill {name: $skill_name})
        RETURN id(s), s.skill_embedding
        LIMIT 1
        """
        result = session.run(query, skill_name=skill_name)
        record = result.single()
        if record:
            return record["id(s)"], record["s.skill_embedding"]
        return None, None

def get_competency_embedding(driver: GraphDatabase.driver, competency_name: str) -> Tuple[int, List[float]]:
    """
    Get embedding for a core competency from the database.
    
    Args:
        driver: Neo4j driver
        competency_name: Name of the core competency
        
    Returns:
        Tuple containing competency ID and embedding
    """
    with driver.session() as session:
        query = """
        MATCH (cc:CoreCompetency {name: $competency_name})
        RETURN id(cc), cc.name, cc.core_competency_embedding
        LIMIT 1
        """
        result = session.run(query, competency_name=competency_name)
        record = result.single()
        if record:
            return record["id(cc)"], record["cc.core_competency_embedding"]
        return None, None

def create_analysis_text(analysis: Analysis) -> str:
    """
    Create a string representation of the analysis.
    
    Args:
        analysis: Analysis object containing job requirements
        
    Returns:
        str: String representation of the analysis
    """
    return f"""Job: {analysis.job_title}
Core Competencies: {', '.join(analysis.core_competencies)}
Skills required: {', '.join(analysis.skills_required)}
Expected experiences: {', '.join(analysis.expected_experiences)}
Success Criteria: {', '.join(analysis.success_criteria)}
Keywords: {', '.join(analysis.most_relevant_keywords)}"""

async def get_skills(analysis: Analysis, accomplishments: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Process skills from the analysis and accomplishments to generate a skills summary.
    
    Args:
        analysis: Analysis object containing job requirements
        accomplishments: Dictionary with company names as keys and lists of accomplishments as values
        
    Returns:
        Dict containing top skills and competencies with their similarity scores
    """
    logger.info("Starting skills processing")
    try:
        # Create and get embeddings for the analysis text
        analysis_text = create_analysis_text(analysis)
        analysis_embedding = get_embeddings(analysis_text)
        logger.info("Generated embeddings for analysis text")
        
        # Extract all unique skills from accomplishments
        all_skills = set()
        for company_accomplishments in accomplishments.values():
            for accomplishment in company_accomplishments:
                all_skills.update(accomplishment["skills"])

        # Extract all unique core competencies from accomplishments
        all_core_competencies = set()
        for company_accomplishments in accomplishments.values():
            for accomplishment in company_accomplishments:
                all_core_competencies.update(accomplishment["core_competencies"])
        
        # Connect to the database
        driver = GraphDatabase.driver(URI, auth=AUTH)
        
        # Calculate similarity scores for skills
        skill_scores = []
        for skill in all_skills:
            skill_id, skill_embedding = get_skill_embedding(driver, skill)
            if skill_embedding:
                similarity = calculate_cosine_similarity(analysis_embedding, skill_embedding)
                skill_scores.append({
                    "id": skill_id,
                    "name": skill,
                    "similarity": similarity
                })
        
        # Calculate similarity scores for core competencies
        competency_scores = []
        for competency in all_core_competencies:
            comp_id, comp_embedding = get_competency_embedding(driver, competency)
            if comp_embedding:
                similarity = calculate_cosine_similarity(analysis_embedding, comp_embedding)
                competency_scores.append({
                    "id": comp_id,
                    "name": competency,
                    "similarity": similarity
                })
        
        # Sort and get top N skills and competencies
        top_skills = sorted(skill_scores, key=lambda x: x["similarity"], reverse=True)[:TOP_N]
        top_competencies = sorted(competency_scores, key=lambda x: x["similarity"], reverse=True)[:TOP_N]
        
        # Create skills summary
        skills_summary = {
            "top_skills": top_skills,
            "top_competencies": top_competencies
        }
        
        # Save skills summary to file
        os.makedirs('inputs', exist_ok=True)
        with open('inputs/04_skills.json', 'w', encoding='utf-8') as f:
            json.dump(skills_summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Skills summary saved to inputs/04_skills.json")
        logger.info(f"Found {len(all_skills)} unique skills and {len(all_core_competencies)} unique core competencies")
        logger.info(f"Calculated similarity scores for top {TOP_N} skills and competencies")
        
        driver.close()
        
        return skills_summary
        
    except Exception as e:
        logger.error(f"Error processing skills: {str(e)}", exc_info=True)
        raise 
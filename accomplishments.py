from neo4j import GraphDatabase
from models import Analysis
from typing import List, Dict, Any, Tuple
from openai import OpenAI
import logging
import os
from dotenv import load_dotenv
# from opik import track, opik_context, Opik
from embeddings import get_embeddings

# Load environment variables
load_dotenv()

# opik_client = Opik()
# Configure logging
logger = logging.getLogger(__name__)

# Constants
COMPANIES = ["8base", "Appify", "Everteam", "Intalio"]
URI = "bolt://localhost:7687"
AUTH = ("", "")

# Configuration from environment variables
VECTOR_SEARCH_TOP_K = int(os.getenv("VECTOR_SEARCH_TOP_K", "3"))

# Similarity thresholds for different types
SKILL_SIMILARITY_THRESHOLD = float(os.getenv("SKILL_SIMILARITY_THRESHOLD", "0.5"))
COMPETENCY_SIMILARITY_THRESHOLD = float(os.getenv("COMPETENCY_SIMILARITY_THRESHOLD", "0.6"))
EXPERIENCE_SIMILARITY_THRESHOLD = float(os.getenv("EXPERIENCE_SIMILARITY_THRESHOLD", "0.4"))

# Adjustment constants for different types of matches
SKILL_MATCH_WEIGHT = float(os.getenv("SKILL_MATCH_WEIGHT", "1.0"))
COMPETENCY_MATCH_WEIGHT = float(os.getenv("COMPETENCY_MATCH_WEIGHT", "1.2"))
EXPERIENCE_MATCH_WEIGHT = float(os.getenv("EXPERIENCE_MATCH_WEIGHT", "1.5"))

def initialize_analysis_scores(analysis: Analysis) -> Dict[str, List[Dict[str, float]]]:
    """Initialize a dictionary with separate lists for skills, competencies, and experiences scores."""
    return {
        "skills": [{"name": skill, "score": 0.0} for skill in analysis.skills_required],
        "core_competencies": [{"name": comp, "score": 0.0} for comp in analysis.core_competencies],
        "experiences": [{"name": exp, "score": 0.0} for exp in analysis.expected_experiences]
    }

def process_neo4j_results(results: Dict[str, List[Dict[str, Any]]], company: str, record: Any, weight: float = 1.0) -> None:
    """
    Process and aggregate results from neo4j query.
    
    Args:
        results: Dictionary to store results
        company: Company name
        record: Neo4j record
        weight: Adjustment weight to apply to similarity score
    """
    # Apply weight to similarity score
    adjusted_similarity = record["similarity"] * weight
    
    accomplishment = {
        "id": record["id"],
        "title": record["title"],
        "body": record["body"],
        "similarity": adjusted_similarity,
        "skills": record["skills"],
        "core_competencies": record["core_competencies"]
    }
    
    # Check if this accomplishment already exists
    existing_acc = next(
        (acc for acc in results[company] if acc["id"] == accomplishment["id"]),
        None
    )
    
    if existing_acc:
        # Update similarity score
        existing_acc["similarity"] += adjusted_similarity
    else:
        # Add new accomplishment
        results[company].append(accomplishment)
    
    # Sort by similarity score
    results[company].sort(key=lambda x: x["similarity"], reverse=True)

def update_analysis_score(analysis_scores: Dict[str, List[Dict[str, float]]], category: str, name: str, similarity: float, weight: float = 1.0) -> None:
    """
    Update the score for a specific item in the analysis scores.
    
    Args:
        analysis_scores: Dictionary containing all scores
        category: Category of the item (skills, core_competencies, or experiences)
        name: Name of the item to update
        similarity: Similarity score to add
        weight: Adjustment weight to apply to similarity score
    """
    # Apply weight to similarity score
    adjusted_similarity = similarity * weight
    
    for item in analysis_scores[category]:
        if item["name"] == name:
            item["score"] += adjusted_similarity
            break

async def retrieve_accomplishment_by_skill(results: Dict[str, List[Dict[str, Any]]], skill: str, analysis_scores: Dict[str, List[Dict[str, float]]]) -> None:
    """
    Retrieve accomplishments related to a skill from the graph database.
    
    Args:
        results: Dictionary to store results
        skill: The skill to search for
        analysis_scores: Dictionary to track similarity scores
    """
    logger.info(f"Starting retrieve_accomplishment_by_skill for skill: {skill}")
    try:
        # trace = opik_client.trace(name=f"retrieve_accomplishment_by_skill", input={"skill": skill}, tags=[os.environ["JOB_RUN"]])
        
        
        # Calculate embeddings for the skill
        skill_embedding = get_embeddings(skill)
        
        # Connect to the database
        driver = GraphDatabase.driver(URI, auth=AUTH)
        with driver.session() as session:
            for company in COMPANIES:
                logger.debug(f"Processing company {company} for skill {skill}")
                # Query for each company
                query = """
                CALL vector_search.search("skill_embedding_index", $top_k, $embedding)
                YIELD node AS skill, similarity
                MATCH (skill)<-[:USED]-(ac:Accomplishment)<-[:ACHIEVED]-(exp:Experience)
                WHERE exp.company = $company AND similarity > $threshold
                WITH ac, MAX(similarity) AS best_similarity
                OPTIONAL MATCH (ac)-[:USED]->(relatedSkill:Skill)
                OPTIONAL MATCH (ac)-[:DEMONSTRATED]->(coreComp:CoreCompetency)
                RETURN id(ac) as id, ac.name as title, ac.body as body, best_similarity AS similarity,
                       COLLECT(DISTINCT relatedSkill.name) AS skills,
                       COLLECT(DISTINCT coreComp.name) AS core_competencies
                ORDER BY similarity DESC;
                """
                
                result = session.run(
                    query, 
                    embedding=skill_embedding, 
                    company=company,
                    top_k=VECTOR_SEARCH_TOP_K,
                    threshold=SKILL_SIMILARITY_THRESHOLD
                )
                
                # Process results for this company
                for record in result:
                    process_neo4j_results(results, company, record, SKILL_MATCH_WEIGHT)
                    # Update skill score
                    update_analysis_score(analysis_scores, "skills", skill, record["similarity"], SKILL_MATCH_WEIGHT)
                    # trace.span(name=f"{company}", input={"skill": skill}, output={"id": record["id"], "title": record["title"], "body": record["body"], "similarity": record["similarity"]})

        driver.close()
        logger.info(f"Completed retrieve_accomplishment_by_skill for skill: {skill}")
        
    except Exception as e:
        logger.error(f"Error retrieving accomplishments for skill {skill}: {str(e)}")

async def retrieve_accomplishment_by_core_competency(results: Dict[str, List[Dict[str, Any]]], competency: str, analysis_scores: Dict[str, List[Dict[str, float]]]) -> None:
    """
    Retrieve accomplishments related to a core competency from the graph database.
    
    Args:
        results: Dictionary to store results
        competency: The core competency to search for
        analysis_scores: Dictionary to track similarity scores
    """
    logger.info(f"Starting retrieve_accomplishment_by_core_competency for competency: {competency}")
    try:
        # trace = opik_client.trace(name=f"retrieve_accomplishment_by_core_competency", input={"competency": competency}, tags=[os.environ["JOB_RUN"]])
        
        # Calculate embeddings for the competency
        competency_embedding = get_embeddings(competency)
        
        # Connect to the database
        driver = GraphDatabase.driver(URI, auth=AUTH)
        
        with driver.session() as session:
            for company in COMPANIES:
                logger.debug(f"Processing company {company} for competency {competency}")
                # Query for each company
                query = """
                CALL vector_search.search("core_competency_embedding_index", $top_k, $embedding)
                YIELD node AS competency, similarity
                MATCH (competency)<-[:DEMONSTRATED]-(ac:Accomplishment)<-[:ACHIEVED]-(exp:Experience)
                WHERE exp.company = $company AND similarity > $threshold
                WITH ac, MAX(similarity) AS best_similarity
                OPTIONAL MATCH (ac)-[:USED]->(relatedSkill:Skill)
                OPTIONAL MATCH (ac)-[:DEMONSTRATED]->(coreComp:CoreCompetency)
                RETURN id(ac) as id, ac.name as title, ac.body as body, best_similarity AS similarity,
                       COLLECT(DISTINCT relatedSkill.name) AS skills,
                       COLLECT(DISTINCT coreComp.name) AS core_competencies
                ORDER BY similarity DESC;
                """
                
                result = session.run(
                    query, 
                    embedding=competency_embedding, 
                    company=company,
                    top_k=VECTOR_SEARCH_TOP_K,
                    threshold=COMPETENCY_SIMILARITY_THRESHOLD
                )
                
                # Process results for this company
                for record in result:
                    process_neo4j_results(results, company, record, COMPETENCY_MATCH_WEIGHT)
                    # Update competency score
                    update_analysis_score(analysis_scores, "core_competencies", competency, record["similarity"], COMPETENCY_MATCH_WEIGHT)
                    # trace.span(name=f"{company}", input={"competency": competency}, output={"id": record["id"], "title": record["title"], "body": record["body"], "similarity": record["similarity"]})
        
        driver.close()
        logger.info(f"Completed retrieve_accomplishment_by_core_competency for competency: {competency}")
        
    except Exception as e:
        logger.error(f"Error retrieving accomplishments for core competency {competency}: {str(e)}")

async def retrieve_accomplishment_by_experience(results: Dict[str, List[Dict[str, Any]]], experience: str, analysis_scores: Dict[str, List[Dict[str, float]]]) -> None:
    """
    Retrieve accomplishments related to an experience requirement from the graph database.
    
    Args:
        results: Dictionary to store results
        experience: The experience requirement to search for
        analysis_scores: Dictionary to track similarity scores
    """
    logger.info(f"Starting retrieve_accomplishment_by_experience for experience: {experience}")
    try:
        # trace = opik_client.trace(name=f"retrieve_accomplishment_by_experience", input={"experience": experience}, tags=[os.environ["JOB_RUN"]])
        
        # Calculate embeddings for the experience
        experience_embedding = get_embeddings(experience)
        
        # Connect to the database
        driver = GraphDatabase.driver(URI, auth=AUTH)
        
        with driver.session() as session:
            for company in COMPANIES:
                logger.debug(f"Processing company {company} for experience {experience}")
                # Query for each company
                query = """
                CALL vector_search.search("accomplishment_embedding_index", $top_k, $embedding)
                YIELD node AS ac, similarity
                MATCH (ac)<-[:ACHIEVED]-(exp:Experience)
                WHERE exp.company = $company AND similarity > $threshold
                WITH ac, MAX(similarity) AS best_similarity
                OPTIONAL MATCH (ac)-[:USED]->(relatedSkill:Skill)
                OPTIONAL MATCH (ac)-[:DEMONSTRATED]->(coreComp:CoreCompetency)
                RETURN id(ac) as id, ac.name as title, ac.body as body, best_similarity AS similarity,
                       COLLECT(DISTINCT relatedSkill.name) AS skills,
                       COLLECT(DISTINCT coreComp.name) AS core_competencies
                ORDER BY similarity DESC;
                """
                
                result = session.run(
                    query, 
                    embedding=experience_embedding, 
                    company=company,
                    top_k=VECTOR_SEARCH_TOP_K,
                    threshold=EXPERIENCE_SIMILARITY_THRESHOLD
                )
                
                # Process results for this company
                for record in result:
                    process_neo4j_results(results, company, record, EXPERIENCE_MATCH_WEIGHT)
                    # Update experience score
                    update_analysis_score(analysis_scores, "experiences", experience, record["similarity"], EXPERIENCE_MATCH_WEIGHT)
                    # trace.span(name=f"{company}", input={"experience": experience}, output={"id": record["id"], "title": record["title"], "body": record["body"], "similarity": record["similarity"]})
        
        driver.close()
        logger.info(f"Completed retrieve_accomplishment_by_experience for experience: {experience}")
        
    except Exception as e:
        logger.error(f"Error retrieving accomplishments for experience {experience}: {str(e)}")

# @track
async def get_accomplishments(analysis: Analysis) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, float]]]]:
    """
    Get relevant accomplishments based on the job analysis.
    
    Args:
        analysis: Analysis object containing job requirements and criteria
        
    Returns:
        Tuple containing:
        - Dictionary with company names as keys and lists of accomplishments as values
        - Dictionary with analysis scores for skills, competencies, and experiences
    """
    logger.info("Starting get_accomplishments")
    try:
        # Initialize results dictionary
        results: Dict[str, List[Dict[str, Any]]] = {company: [] for company in COMPANIES}
        
        # Initialize analysis scores
        analysis_scores = initialize_analysis_scores(analysis)
        
        # Process skills
        for skill in analysis.skills_required:
            await retrieve_accomplishment_by_skill(results, skill, analysis_scores)
            
        # Process core competencies
        for competency in analysis.core_competencies:
            await retrieve_accomplishment_by_core_competency(results, competency, analysis_scores)
            
        # Process experience requirements
        for experience in analysis.expected_experiences:
            await retrieve_accomplishment_by_experience(results, experience, analysis_scores)
        
        # opik_context.update_current_trace(tags=[os.environ["JOB_RUN"]])
        logger.info("Completed get_accomplishments")
        return results, analysis_scores
        
    except Exception as e:
        logger.error(f"Error in get_accomplishments: {str(e)}")
        raise e

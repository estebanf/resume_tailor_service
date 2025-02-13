from pymongo import MongoClient
from html_utils import process_job_html
from url_utils import extract_job_id
from analysis import analyze_job_post
from accomplishments import get_accomplishments, COMPANIES
from skills import get_skills
from resume_headers import get_key_skills, get_professional_summary
from tailor_resume import improve_accomplishments_labels
from render import render_resume
from models import Analysis
from typing import Optional, Dict, List
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import logging
import json
import os

# Use root logger
logger = logging.getLogger()

# Validation Constants
MIN_ACCOMPLISHMENTS = {
    "8base": 4,
    "Appify": 2,
    "Everteam": 4,
    "Intalio": 4
}

# Minimum ratio of skills/competencies/experiences that should have scores > 0
MIN_SKILLS_SCORE_RATIO = 0.5
MIN_COMPETENCIES_SCORE_RATIO = 0.5
MIN_EXPERIENCES_SCORE_RATIO = 0.1

class JobPost(BaseModel):
    html: str
    url: HttpUrl
    timestamp: datetime

def validate_accomplishments_count(accomplishments: Dict[str, List[Dict]]) -> bool:
    """
    Validate that each company has the minimum required number of accomplishments.
    
    Args:
        accomplishments: Dictionary with company names as keys and lists of accomplishments as values
        
    Returns:
        bool: True if all companies meet their minimum requirements
    """
    for company, min_count in MIN_ACCOMPLISHMENTS.items():
        if len(accomplishments.get(company, [])) < min_count:
            logger.warning(f"{company} has {len(accomplishments.get(company, []))} accomplishments, minimum required is {min_count}")
            return False
    return True

def validate_analysis_scores(scores: Dict[str, List[Dict[str, float]]]) -> bool:
    """
    Validate that enough items in each category have scores above zero.
    
    Args:
        scores: Dictionary containing scores for skills, competencies, and experiences
        
    Returns:
        bool: True if all categories meet their minimum ratio requirements
    """
    # Check skills
    skills_with_scores = sum(1 for skill in scores["skills"] if skill["score"] > 0)
    skills_ratio = skills_with_scores / len(scores["skills"]) if scores["skills"] else 0
    if skills_ratio < MIN_SKILLS_SCORE_RATIO:
        logger.warning(f"Only {skills_ratio:.2%} of skills have scores > 0, minimum required is {MIN_SKILLS_SCORE_RATIO:.2%}")
        return False

    # Check competencies
    comp_with_scores = sum(1 for comp in scores["core_competencies"] if comp["score"] > 0)
    comp_ratio = comp_with_scores / len(scores["core_competencies"]) if scores["core_competencies"] else 0
    if comp_ratio < MIN_COMPETENCIES_SCORE_RATIO:
        logger.warning(f"Only {comp_ratio:.2%} of competencies have scores > 0, minimum required is {MIN_COMPETENCIES_SCORE_RATIO:.2%}")
        return False

    # Check experiences
    exp_with_scores = sum(1 for exp in scores["experiences"] if exp["score"] > 0)
    exp_ratio = exp_with_scores / len(scores["experiences"]) if scores["experiences"] else 0
    if exp_ratio < MIN_EXPERIENCES_SCORE_RATIO:
        logger.warning(f"Only {exp_ratio:.2%} of experiences have scores > 0, minimum required is {MIN_EXPERIENCES_SCORE_RATIO:.2%}")
        return False

    return True

async def intake_job_post(job_post: JobPost) -> None:
    """
    Process a job post in the background.
    This function handles the extraction of the job ID and processing of HTML content.
    """
    try:
        # Delete all the files in the inputs directory
        for file in os.listdir('inputs'):
            os.remove(f'inputs/{file}')

        logger.info("Starting job post processing")
        
        # Extract clean URL
        clean_url = extract_job_id(str(job_post.url))
        if clean_url:
            logger.info(f"Original URL: {job_post.url}")
            logger.info(f"Cleaned URL: {clean_url}")
        else:
            logger.warning("Could not extract job ID from URL")
            return
        
        # Process HTML content
        processed_html = await process_job_html(job_post.html)
        if not processed_html:
            logger.warning("No HTML content was processed")
            return
            
        logger.info(f"Processed HTML length: {len(processed_html)} characters")
        logger.debug(f"First 100 chars: {processed_html[:100]}")
        
        # Create inputs directory if it doesn't exist
        os.makedirs('inputs', exist_ok=True)
        
        # Save the url to a file
        with open('inputs/00_url.txt', 'w', encoding='utf-8') as f:
            f.write(str(clean_url))
        logger.info("URL saved to inputs/00_url.txt")

        # Save processed HTML to text file
        with open('inputs/01_job_post.txt', 'w', encoding='utf-8') as f:
            f.write(processed_html)
        logger.info("Processed job post saved to inputs/01_job_post.txt")

        await analyse_job_post(clean_url, processed_html)
        
    except Exception as e:
        logger.error(f"Error processing job post: {str(e)}", exc_info=True)

async def analyse_job_post(clean_url: str = None, processed_html: str = None) -> None:
    """
    Analyze a job post and save the analysis results.
    
    Args:
        clean_url: Optional cleaned URL string
        processed_html: Optional processed HTML content
    """
    try:
        # If arguments are not provided, read from files
        if clean_url is None:
            with open('inputs/00_url.txt', 'r', encoding='utf-8') as f:
                clean_url = f.read().strip()
                
        if processed_html is None:
            with open('inputs/01_job_post.txt', 'r', encoding='utf-8') as f:
                processed_html = f.read()
        
        # Analyze the processed content
        analysis_result = await analyze_job_post(processed_html)
        if not analysis_result:
            logger.warning("Job post analysis failed")
            return
            
        logger.info(f"Analysis completed successfully for job: {analysis_result.job_title} at {analysis_result.company_name}")
        
        # Save analysis result to JSON file
        with open('inputs/02_analysis_result.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info("Analysis result saved to inputs/02_analysis_result.json")

        await process_job_post(clean_url, processed_html, analysis_result)
        
    except Exception as e:
        logger.error(f"Error analyzing job post: {str(e)}", exc_info=True)

async def process_job_post(clean_url: str = None, processed_html: str = None, analysis_result: Analysis = None) -> None:
    """
    Process a job post using either provided content or reading from files.
    
    Args:
        clean_url: Optional cleaned URL string
        processed_html: Optional processed HTML content
        analysis_result: Optional Analysis object
    """
    try:
        # If arguments are not provided, read from files
        if clean_url is None:
            with open('inputs/00_url.txt', 'r', encoding='utf-8') as f:
                clean_url = f.read().strip()
                
        if processed_html is None:
            with open('inputs/01_job_post.txt', 'r', encoding='utf-8') as f:
                processed_html = f.read()

        if analysis_result is None:
            with open('inputs/02_analysis_result.json', 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
                analysis_result = Analysis(**analysis_data)
        
        # Get accomplishments based on analysis
        accomplishments, analysis_scores = await get_accomplishments(analysis_result)
        logger.info("Retrieved accomplishments from database")

        # Save accomplishments and scores to JSON file
        accomplishment_data = {
            "accomplishments": accomplishments,
            "analysis_scores": analysis_scores
        }
        with open('inputs/03_accomplishments.json', 'w', encoding='utf-8') as f:
            json.dump(accomplishment_data, f, indent=2, ensure_ascii=False)
        logger.info("Accomplishments and scores saved to inputs/03_accomplishments.json")

        # Validate results
        if not validate_accomplishments_count(accomplishments):
            logger.error("Failed to meet minimum accomplishments requirements")
            return
            
        if not validate_analysis_scores(analysis_scores):
            logger.error("Failed to meet minimum score requirements")
            return
        
        logger.info("Analysis results meet all validation criteria")
        
        # Process skills
        skills_summary = await get_skills(analysis_result, accomplishments)
        logger.info("Skills processing completed")
        
        # Generate key skills
        key_skills = await get_key_skills(analysis_result, skills_summary)
        logger.info("Generated key skills")
        
        # Save key skills to file
        with open('inputs/05_key_skills.json', 'w', encoding='utf-8') as f:
            json.dump(key_skills.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info("Key skills saved to inputs/05_key_skills.json")
        
        # Generate professional summary
        professional_summary = await get_professional_summary(
            processed_html, 
            accomplishments,
            key_skills,
            analysis_result
        )
        logger.info("Generated professional summary")
        
        # Save professional summary to file
        with open('inputs/06_professional_summary.json', 'w', encoding='utf-8') as f:
            json.dump(professional_summary.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info("Professional summary saved to inputs/06_professional_summary.json")
        
        # Assemble resume data
        resume_data = {
            "professional_summary": professional_summary.summary,
            "key_skills": [s.skill for s in key_skills.skills],
            "eight_base": [
                {"label": acc["title"], "details": acc["body"]} 
                for acc in accomplishments["8base"][:5]
            ],
            "appify": [
                {"label": acc["title"], "details": acc["body"]} 
                for acc in accomplishments["Appify"][:2]
            ],
            "everteam": [
                {"label": acc["title"], "details": acc["body"]} 
                for acc in accomplishments["Everteam"][:4]
            ],
            "intalio": [
                {"label": acc["title"], "details": acc["body"]} 
                for acc in accomplishments["Intalio"][:4]
            ]
        }
        
        # Improve accomplishment labels
        improved_labels = await improve_accomplishments_labels(analysis_result, resume_data)
        
        # Update labels in resume_data
        for i, label in enumerate(improved_labels.eight_base):
            resume_data["eight_base"][i]["label"] = label
        for i, label in enumerate(improved_labels.appify):
            resume_data["appify"][i]["label"] = label
        for i, label in enumerate(improved_labels.everteam):
            resume_data["everteam"][i]["label"] = label
        for i, label in enumerate(improved_labels.intalio):
            resume_data["intalio"][i]["label"] = label
        
        # Save resume data
        with open('inputs/04_resume.json', 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2, ensure_ascii=False)
        logger.info("Resume data saved to inputs/04_resume.json")
        
        # Assemble analysis data for render
        analysis_data = {
            "company_name": analysis_result.company_name,
            "job_title": analysis_result.job_title
        }
        
        # Render the resume
        render_resume(resume_data, analysis_data)
        logger.info("Resume rendered successfully")

        # MongoDB connection
        client = MongoClient('mongodb://localhost:27017/')
        db = client['job_hunt']
        collection = db['applications']

        now = datetime.utcnow()
        document = {
            'job_post': processed_html,
            'analysis_data': analysis_result.model_dump(),
            'accomplishments': accomplishments,
            'resume_data': resume_data,
            'created_at': now,
            'updated_at': now
        }

        # Store document
        collection.insert_one(document)

        logger.info("Job post processing completed")
        
    except Exception as e:
        logger.error(f"Error processing job post: {str(e)}", exc_info=True) 
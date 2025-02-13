from typing import List, Dict, Any
from pydantic import BaseModel, Field
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import logging
import json
import os
from models import Analysis, TopSkills, ProfessionalSummary

# Configure logging
logger = logging.getLogger(__name__)

class KeySkillsInput(BaseModel):
    job_title: str = Field(description="The title of the job")
    success_criteria: List[str] = Field(description="The success criteria for the role")
    relevant_keywords: List[str] = Field(description="The most relevant keywords from the job post")
    top_skills: List[str] = Field(description="The top skills identified for the candidate")
    top_competencies: List[str] = Field(description="The top competencies identified for the candidate")

class ProfessionalSummaryInput(BaseModel):
    job_post: str = Field(description="The full job post text")
    key_skills: List[str] = Field(description="The key skills identified for the resume")
    resume_accomplishments: List[str] = Field(description="List of accomplishment summaries with title and body")
    success_criteria: List[str] = Field(description="The success criteria for the role")
    keywords: List[str] = Field(description="The most relevant keywords from the job post")

def save_prompt(prompt_template: PromptTemplate, input_data: Dict[str, Any], filename: str) -> None:
    """
    Save the prompt template and formatted prompt to a file.
    
    Args:
        prompt_template: The template string before formatting
        input_data: The input data used to format the template
        filename: Name of the file to save to
    """
    os.makedirs('prompts', exist_ok=True)
    content = formatted_prompt = prompt_template.format(**input_data)
    
    with open(f'prompts/{filename}', 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"Prompt saved to prompts/{filename}")

async def get_key_skills(analysis: Analysis, skills_summary: Dict[str, List[Dict[str, Any]]]) -> TopSkills:
    """
    Generate key skills for the resume based on job requirements and candidate's skills.
    
    Args:
        analysis: Analysis object containing job requirements
        skills_summary: Dictionary containing top skills and competencies
        
    Returns:
        TopSkills object containing the list of key skills
    """
    logger.info("Starting to generate key skills")
    try:
        # Extract skill names
        top_skills = [skill["name"] for skill in skills_summary["top_skills"]]
        top_competencies = [comp["name"] for comp in skills_summary["top_competencies"]]
        
        # Create input model
        input_data = KeySkillsInput(
            job_title=analysis.job_title,
            success_criteria=analysis.success_criteria,
            relevant_keywords=analysis.most_relevant_keywords,
            top_skills=top_skills,
            top_competencies=top_competencies
        )
        
        # Create the prompt template
        template = PromptTemplate.from_template(
            """You are an expert resume writer with a special talent to identify and craft the most impactful professional skill section.

The role the candidate is applying is: `{job_title}`
After analyzing the job post, you determined the success criteria for the role is
```json
{success_criteria}
```
The most relevant keywords from the job post are
```json
{relevant_keywords}
```

In the resume, the accomplishments the candidate will present allow the reader to infer the candidate has the following skills
```json
{top_skills}
```
And these core competencies
```json
{top_competencies}
```
A professional skill represents a candidate's skill or core competency expressed in 3 words or less, followed by the actual candidate's skill or core competency that is being referenced. Identify the top 12 professional skills most aligned with the job post success criteria. The selected skills should be explicitly covered by the candidate's list of skills and core competencies. Do not add skills just because the success criteria require it if it is not absolutely crystal clear the candidate possesses them.""")
        # Save the prompt
        save_prompt(template, input_data.model_dump(), "key_skills_prompt.txt")
        
        # Create the model
        model = template | ChatOpenAI(
            model="gpt-4o",
            temperature=0.5
        ).with_structured_output(TopSkills)
        
        # Get the response
        result = await model.ainvoke(input_data.model_dump())
        
        logger.info("Successfully generated key skills")
        return result
        
    except Exception as e:
        logger.error(f"Error generating key skills: {str(e)}", exc_info=True)
        raise

async def get_professional_summary(job_post: str, accomplishments: Dict[str, List[Dict[str, Any]]], 
                                 top_skills: TopSkills, analysis: Analysis) -> ProfessionalSummary:
    """
    Generate a professional summary based on job requirements and candidate's experience.
    
    Args:
        job_post: The job post text
        accomplishments: Dictionary containing accomplishments by company
        top_skills: TopSkills object containing key skills
        analysis: Analysis object containing job requirements
        
    Returns:
        ProfessionalSummary object containing the summary text
    """
    logger.info("Starting to generate professional summary")
    try:
        # Extract accomplishment summaries
        accomplishment_summaries = []
        for company, company_accomplishments in accomplishments.items():
            for acc in company_accomplishments:
                accomplishment_summaries.append(f"{acc['title']}: {acc['body']}")
        
        # Create input model
        input_data = ProfessionalSummaryInput(
            job_post=job_post,
            key_skills=[s.skill for s in top_skills.skills],
            resume_accomplishments=accomplishment_summaries,
            success_criteria=analysis.success_criteria,
            keywords=analysis.most_relevant_keywords
        )
        
        # Create the prompt template
        template = PromptTemplate.from_template(
            """You are an expert resume writer with a special talent to identify and craft the most impactful professional summary.

You analyzed the job post and determined the success criteria for the role is
```json
{success_criteria}
```

You also identified the most relevant keywords from the job post are
```json
{keywords}
```

The candidate's will present these professional skills:
```json
{key_skills}
```

The resume will also include these accomplishments:
```json
{resume_accomplishments}
```

Your job is to write a professional summary that will give the reader confidence the candidate can satisfy these success criteria. Here are some examples of professional summaries the candidate has used in the past:
```
Driven product leader with 15+ years of success orchestrating SaaS product strategies, solution engineering, and enterprise IT architecture. Delivers AI-driven product innovations and cross-functional collaboration to achieve exceptional market results. Skilled at leveraging data-driven insights and user research to align features with customer needs and drive adoption. Adept at bridging complex technical requirements with strategic business goals while fostering accountability and transparent communication. Recognized for orchestrating collaborative teams that deliver compelling user experiences and build strong customer loyalty.
```
---
```
Seasoned product leader with over 15 years of experience driving product strategies for SaaS and enterprise solutions. Adept at integrating AI, cloud, and process automation to bring innovative offerings to market. Skilled at cultivating cross-functional teams, identifying market opportunities, and guiding products through full lifecycles. Excels in balancing hands-on technical insight with strong stakeholder engagement. Recognized for empathetic leadership, data-driven decision-making, and timely execution that exceeds customer and business expectations.
```
---
```
Seasoned product and solution engineering leader with over 15 years in B2B SaaS, bridging advanced technical knowledge with strategic leadership. Over the course of multiple acquisitions and product launches, excels at orchestrating cross-functional teams to deliver data-driven innovations at global scale. Adept at guiding organizations through complex transitions, aligning stakeholders around unified goals, and maximizing business outcomes. Recognized for operational excellence, empathy-based leadership, and an unwavering focus on customer needs. Equips teams with streamlined processes, scalable platforms, and robust strategies that propel revenue growth and market impact.
```
---
```
Seasoned solutions engineering leader with over 15 years of enterprise experience bridging business and technology. Skilled in leading cross-functional teams, mentoring staff, and delivering impactful product innovations. Demonstrated success in data integration, AI/ML, low-code platforms, and process automation across multiple acquisitions. Adept at building collaborative relationships with stakeholders to drive adoption, enhance product offerings, and maintain operational excellence. Combines hands-on technical knowledge with strong business acumen to consistently exceed organizational goals.
```
---

Write a professional summary mimicking the tone, style, length and sentence structure of the examples above, with a maximum of five sentences. Professional summary should be factual and based on the candidate's experience and skills and aligned with the job post, success criteria and keywords. Do not make any claim about the candidate that is not clearly reflected in the accomplishments and skills. Do not let keywords and success criteria drive what you write. Follow these rules

- The professional summary must strictly reflect the candidate’s experience and accomplishments. Do not infer or assume expertise outside of explicitly stated skills and accomplishments.
- Use job post keywords only when directly supported by the candidate’s documented experience. Do not force-fit keywords or assume expertise.
- Every claim in the professional summary must be clearly supported by an accomplishment or skill provided. Do not generalize expertise beyond what is explicitly stated.
- Avoid using metrics or numbers in the professional summary.
- Do not quote the accomplishments directly, but focus on the candidate's role and impact of its skills and core competencies.


""")
        
        # Save the prompt
        save_prompt(template, input_data.model_dump(), "professional_summary_prompt.txt")
        
        # Create the model
        model = template | ChatOpenAI(
            model="gpt-4o",
            temperature=0.5
        ).with_structured_output(ProfessionalSummary)
        
        # Get the response
        result = await model.ainvoke(input_data.model_dump())
        
        logger.info("Successfully generated professional summary")
        return result
        
    except Exception as e:
        logger.error(f"Error generating professional summary: {str(e)}", exc_info=True)
        raise 
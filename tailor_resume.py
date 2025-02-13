from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import logging
import os
import json
from models import Analysis, AccomplishmentLabels

# Configure logging
logger = logging.getLogger(__name__)

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

def format_accomplishments(resume_data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """Format all accomplishments into a dictionary for the prompt."""
    return {
        "8base": [
            {"label": acc["label"], "details": acc["details"]}
            for acc in resume_data['eight_base']
        ],
        "appify": [
            {"label": acc["label"], "details": acc["details"]}
            for acc in resume_data['appify']
        ],
        "everteam": [
            {"label": acc["label"], "details": acc["details"]}
            for acc in resume_data['everteam']
        ],
        "intalio": [
            {"label": acc["label"], "details": acc["details"]}
            for acc in resume_data['intalio']
        ]
    }

async def improve_accomplishments_labels(analysis_result: Analysis, resume_data: Dict[str, Any]) -> AccomplishmentLabels:
    """
    Improve the labels of accomplishments to better align with job requirements.
    
    Args:
        analysis_result: Analysis object containing job requirements
        resume_data: Dictionary containing resume content
        
    Returns:
        AccomplishmentLabels object containing improved labels for each company
    """
    logger.info("Starting to improve accomplishment labels")
    
    # Create input data for the prompt
    input_data = {
        "core_competencies": json.dumps(analysis_result.core_competencies),
        "skills_required": json.dumps(analysis_result.skills_required),
        "most_relevant_keywords": json.dumps(analysis_result.most_relevant_keywords),
        "professional_summary": resume_data['professional_summary'],
        "key_skills": json.dumps(resume_data['key_skills']),
        "accomplishments": json.dumps(format_accomplishments(resume_data), indent=2)
    }
    
    # Create the prompt template
    template = PromptTemplate.from_template(
        """You are an expert in tailoring resumes to maximize alignment with the job post

You previously analyzed the job post and concluded these are the most important elements of it

**  Core Competencies **
```json
{core_competencies}
```
**  Skills required **
```json
{skills_required}
```
** Most Relevant Keywords **
```json
{most_relevant_keywords}
```

This is the current information in the resume

** Professional Summary **
```
{professional_summary}
```

Key skills
```json
{key_skills}
```

Accomplishments
```json
{accomplishments}
```

Each accomplishment has a label. Your job is to provide a list of updated labels to maximize alignment of the professional summary, key skills, and accomplishments with the keywords, core competencies, and required skills of the job post.

Make sure to follow the rules
- Provide only the list of updated labels
- Make sure to return as many labels as accomplishments and in the same order
- Make sure the labels is aligned and factual to the accomplishment it describes.
- Each label cannot be longer than 4 words.
- The label should not repeat what the accomplishment says
- For the resume to be readable, labels should not repeat or be too similar""")
    
    # Save the prompt
    save_prompt(template, input_data, "tailor_resume_prompt.txt")
    
    # Create the model
    model = template | ChatOpenAI(
        model="gpt-4o",
        temperature=0.5
    ).with_structured_output(AccomplishmentLabels)
    
    max_retries = 3
    attempt = 1
    last_error = None

    while attempt <= max_retries + 1:
        try:
            # Get the response
            result = await model.ainvoke(input_data)
            
            # Validate the number of labels matches the number of accomplishments
            if (len(result.eight_base) != len(resume_data['eight_base']) or
                len(result.appify) != len(resume_data['appify']) or
                len(result.everteam) != len(resume_data['everteam']) or
                len(result.intalio) != len(resume_data['intalio'])):
                
                error_msg = (
                    f"Number of labels does not match number of accomplishments. "
                    f"Expected: 8base={len(resume_data['eight_base'])}, "
                    f"appify={len(resume_data['appify'])}, "
                    f"everteam={len(resume_data['everteam'])}, "
                    f"intalio={len(resume_data['intalio'])}. "
                    f"Got: 8base={len(result.eight_base)}, "
                    f"appify={len(result.appify)}, "
                    f"everteam={len(result.everteam)}, "
                    f"intalio={len(result.intalio)}"
                )
                
                if attempt <= max_retries:
                    logger.warning(f"Validation failed on attempt {attempt}/{max_retries}: {error_msg}")
                    attempt += 1
                    continue
                else:
                    raise ValueError(error_msg)
            
            logger.info("Successfully generated improved accomplishment labels")
            return result
            
        except Exception as e:
            last_error = str(e)
            if attempt <= max_retries:
                logger.warning(f"Error on attempt {attempt}/{max_retries}: {last_error}")
                attempt += 1
            else:
                logger.error(f"All attempts failed. Last error: {last_error}")
                raise 
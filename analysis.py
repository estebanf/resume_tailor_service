import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import Optional
# from opik import track, opik_context
# import opik
from models import Analysis

# Load environment variables
load_dotenv()

# Initialize Opik
# opik.configure(use_local=False)

# Create the prompt template
template = PromptTemplate.from_template("""
### Task:
Extract structured information from the following job post, including the company name, role name, core competencies, required skills, expected experience, most relevant keywords, and success criteria.

### **Guidelines for Extraction:**

#### **1. Core Competencies**
- Identify the **fundamental abilities, knowledge areas, and strategic attributes** required for the role.
- Extract competencies from **responsibilities, leadership expectations, and business acumen mentions.**
- Focus on **high-level skills like strategic thinking, decision-making, stakeholder engagement, and leadership.**

#### **2. Skills Required**
- Extract **specific technical and soft skills** that are teachable and actionable.
- Identify **technologies, frameworks, and methodologies** explicitly mentioned.
- Include **interpersonal and leadership skills** such as communication, negotiation, and stakeholder management.
- Ensure all skills are **directly linked to job responsibilities and qualifications.**

#### **3. Expected Experience**
- Identify **education level, years of experience, and certifications** required.
- Extract **industry knowledge, tools, and relevant methodologies** mentioned in the job post.
- Capture **specific domains or tools** that candidates should be familiar with.

#### **4. Most Relevant Keywords**
- Extract **frequently mentioned words and phrases** critical for ATS (Applicant Tracking System) optimization.
- Identify **industry-specific terminology, methodologies, and strategic functions** appearing multiple times.
- Include **job scope-related keywords** that define the essence of the role.

#### **5. Success Criteria**
- Identify measurable outcomes that define success in the role.
- Look for **specific deliverables, KPIs, or expectations** set by the company.
- Capture strategic priorities related to **market growth, product success, customer engagement, and operational excellence.**

### **Instructions:**
- Analyze the following job post. Be comprehensive and detailed in your analysis, ensuring that you are capturing as much relevant information as possible. More entries are better than less:
  
```text
{job_post}
```
""")

def save_prompt(prompt: str, job_post_text: str):
    """Save the formatted prompt to a file."""
    # Create prompts directory if it doesn't exist
    os.makedirs('prompts', exist_ok=True)
    
    # Write the prompt to file
    with open('prompts/job_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(prompt)

# @opik.track
async def analyze_job_post(job_post_text: str) -> Optional[Analysis]:
    """
    Analyze a job post text and return structured information about it.
    
    Args:
        job_post_text: The cleaned text content of the job post
        
    Returns:
        Analysis object containing structured information about the job post
    """
    try:
        # Format the prompt with the job post text
        prompt = template.format(job_post=job_post_text)
        
        # Save the prompt to file
        save_prompt(prompt, job_post_text)
        
        # Initialize the ChatOpenAI client with gpt-4o-mini
        model = template | ChatOpenAI(
            model="gpt-4o",
            temperature=0.5
        ).with_structured_output(Analysis) 
        
        # # Start an Opik span for job analysis
        # span.set_attribute("job_post_length", len(job_post_text))
        
        # Get the response from the model with structured output
        result = await model.ainvoke({"job_post": job_post_text})
        
        # set environment variable
        os.environ["JOB_RUN"] = f'{result.company_name} - {result.job_title}'
        # opik_context.update_current_trace(tags=[os.environ["JOB_RUN"]])
        # # Log the full result as a JSON string
        # span.set_attribute("analysis_result", json.dumps(result.model_dump()))
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error analyzing job post: {error_msg}")
        
        # Log the error with Opik
        # with opik.trace("job_analysis_error") as error_span:
        #     error_span.set_attribute("error", error_msg)
        #     error_span.set_status(opik.Status(opik.StatusCode.ERROR, error_msg))
        
        return None

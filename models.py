from pydantic import BaseModel, Field
from typing import List

class Analysis(BaseModel):
    company_name: str = Field(description="The name of the company")
    job_title: str = Field(description="The title of the job")
    core_competencies: list[str] = Field(description="The sorted list of core competencies required in the job post")
    skills_required: list[str] = Field(description="The sorted list of skills that appear in the job post")
    expected_experiences: list[str] = Field(description="The prior work history, education, or certifications needed to be eligible for the role")
    most_relevant_keywords: list[str] = Field(description="The sorted list of most relevant keywords from the job post")
    success_criteria: list[str] = Field(description="The sorted list of success criteria for the job post")

class Skill(BaseModel):
    skill: str = Field(description="The professional skill to include in the resume. It should be 3 words or less")
    candidate_skill_or_core_competency: str = Field(description="The actual skill or core competency that the candidate possesses that is being referenced")

class TopSkills(BaseModel):
    skills: list[Skill] = Field(description="List of key skills for the resume")

class ProfessionalSummary(BaseModel):
    summary: str = Field(description="Professional summary text for the resume") 

class AccomplishmentLabels(BaseModel):
    eight_base: List[str] = Field(description="Labels for the accomplishments at 8base")
    appify: List[str] = Field(description="Labels for the accomplishments at appify")
    everteam: List[str] = Field(description="Labels for the accomplishments at everteam")
    intalio: List[str] = Field(description="Labels for the accomplishments at intalio")

class CompanyResearch(BaseModel):
    overview: str = Field(description="A short paragraph (1-3 sentences) summarizing the company")
    mission: str = Field(description="A short paragraph (1-3 sentences) summarizing the company's mission")
    values: list[str] = Field(description="A list of the company's values")
    financial_health: str = Field(description="A short paragraph (1-3 sentences) summarizing the company's financial health")
    market_penetration: str = Field(description="A short paragraph (1-3 sentences) summarizing the company's market penetration")
    competitors: list[str] = Field(description="A list of the company's competitors")
    challenges: list[str] = Field(description="A list of the company's challenges")
    opportunities: list[str] = Field(description="A list of the company's opportunities")

class CoreCompetenciesEntry(BaseModel):
    title: str = Field(description="The title of the core competency or experience")
    details: str = Field(description="A short paragraph (3-5 sentences) describing the core competency or experience that is relevant to the role")

class CoreCompetenciesSection(BaseModel):
    intro_paragraph: str = Field(description="The intro paragraph of the core competencies section")
    core_competencies: list[CoreCompetenciesEntry] = Field(description="A list of core competencies for the resume")

class CoverLetter(BaseModel):
    opening_paragraph: str = Field(description="The opening paragraph of the cover letter")
    core_competencies_paragraph: CoreCompetenciesSection = Field(description="The core competencies paragraph of the cover letter")
    value_alignment_paragraph: str = Field(description="The value alignment paragraph of the cover letter")
    call_to_action_paragraph: str = Field(description="The call to action paragraph of the cover letter")
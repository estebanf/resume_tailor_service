from fastapi import FastAPI, HTTPException, APIRouter
from neo4j import GraphDatabase
from pydantic import BaseModel
from typing import List, Optional
from embeddings import get_embeddings
import logging
from fastapi import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Neo4j driver
driver = GraphDatabase.driver("bolt://localhost:7687")

# Pydantic models
class SearchQuery(BaseModel):
    query: str

class Skill(BaseModel):
    name: str

class CoreCompetency(BaseModel):
    name: str

class Accomplishment(BaseModel):
    id: int
    name: str
    body: str

class AccomplishmentUpdate(BaseModel):
    name: str
    body: str

class SkillWithId(BaseModel):
    id: int
    name: str
    similarity: Optional[float] = None

class CoreCompetencyWithId(BaseModel):
    id: int
    name: str
    similarity: Optional[float] = None

class Experience(BaseModel):
    id: int
    name: str
    company: str

class CreateAccomplishment(BaseModel):
    name: str
    body: str
    experience_id: int

router = APIRouter(
    prefix="/api/data",
    tags=["data"],
    responses={404: {"description": "Not found"}},
)

@router.get("/accomplishments/{company}", 
         summary="Get accomplishments by company",
         description="Retrieve all accomplishments associated with a specific company")
async def get_accomplishments(
    company: str = Path(..., description="The name of the company to get accomplishments for")
) -> List[Accomplishment]:
    """
    Get all accomplishments for a specific company.
    
    Parameters:
    - company: The name of the company
    
    Returns:
    - List of accomplishments with their IDs and names
    """
    query = """
    MATCH (acc:Accomplishment)<-[a:ACHIEVED]-(exp:Experience {company: $company})
    RETURN id(acc) as id, acc.name as name, acc.body as body
    """
    try:
        with driver.session() as session:
            result = session.run(query, company=company)
            return [Accomplishment(id=record["id"], name=record["name"], body=record["body"]) 
                   for record in result]
    except Exception as e:
        logger.error(f"Error getting accomplishments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accomplishments/{accomplishment_id}/skills")
async def get_accomplishment_skills(accomplishment_id: int) -> List[SkillWithId]:
    query = """
    MATCH (s:Skill)<-[:USED]-(acc:Accomplishment)
    WHERE id(acc) = $accomplishment_id
    RETURN id(s) as id, s.name as name
    """
    try:
        with driver.session() as session:
            result = session.run(query, accomplishment_id=accomplishment_id)
            return [SkillWithId(id=record["id"], name=record["name"]) 
                   for record in result]
    except Exception as e:
        logger.error(f"Error getting skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accomplishments/{accomplishment_id}/core_competencies")
async def get_accomplishment_competencies(accomplishment_id: int) -> List[CoreCompetencyWithId]:
    query = """
    MATCH (cc:CoreCompetency)<-[:DEMONSTRATED]-(acc:Accomplishment)
    WHERE id(acc) = $accomplishment_id
    RETURN id(cc) as id, cc.name as name
    """
    try:
        with driver.session() as session:
            result = session.run(query, accomplishment_id=accomplishment_id)
            return [CoreCompetencyWithId(id=record["id"], name=record["name"]) 
                   for record in result]
    except Exception as e:
        logger.error(f"Error getting core competencies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/skills")
async def search_skills(query: SearchQuery) -> List[SkillWithId]:
    try:
        # Calculate embeddings for the search query
        vector = get_embeddings(query.query)
        
        # Search using vector index
        search_query = """
        CALL vector_search.search("skill_embedding_index", 3, $vector)
        YIELD node AS s, similarity
        RETURN id(s) as id, s.name as name, similarity
        """
        with driver.session() as session:
            result = session.run(search_query, vector=vector)
            return [SkillWithId(id=record["id"], name=record["name"], similarity=record["similarity"]) 
                   for record in result]
    except Exception as e:
        logger.error(f"Error searching skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/core_competencies")
async def search_core_competencies(query: SearchQuery) -> List[CoreCompetencyWithId]:
    try:
        # Calculate embeddings for the search query
        vector = get_embeddings(query.query)
        
        # Search using vector index
        search_query = """
        CALL vector_search.search("core_competency_embedding_index", 3, $vector)
        YIELD node AS cc, similarity
        RETURN id(cc) as id, cc.name as name, similarity
        """
        with driver.session() as session:
            result = session.run(search_query, vector=vector)
            return [CoreCompetencyWithId(id=record["id"], name=record["name"], similarity=record["similarity"]) 
                   for record in result]
    except Exception as e:
        logger.error(f"Error searching core competencies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/accomplishment/{accomplishment_id}/used/{skill_id}")
async def link_skill_to_accomplishment(accomplishment_id: int, skill_id: int) -> dict[str, str]:
    query = """
    MATCH (acc:Accomplishment), (s:Skill)
    WHERE id(acc) = $accomplishment_id AND id(s) = $skill_id
    CREATE (acc)-[:USED]->(s)
    """
    try:
        with driver.session() as session:
            session.run(query, accomplishment_id=accomplishment_id, skill_id=skill_id)
            return {"message": "Relationship created successfully"}
    except Exception as e:
        logger.error(f"Error linking skill to accomplishment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/accomplishment/{accomplishment_id}/demonstrated/{core_competency_id}")
async def link_competency_to_accomplishment(accomplishment_id: int, core_competency_id: int) -> dict[str, str]:
    query = """
    MATCH (acc:Accomplishment), (cc:CoreCompetency)
    WHERE id(acc) = $accomplishment_id AND id(cc) = $core_competency_id
    CREATE (acc)-[:DEMONSTRATED]->(cc)
    """
    try:
        with driver.session() as session:
            session.run(query, accomplishment_id=accomplishment_id, core_competency_id=core_competency_id)
            return {"message": "Relationship created successfully"}
    except Exception as e:
        logger.error(f"Error linking core competency to accomplishment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/skills")
async def create_skill(skill: Skill) -> SkillWithId:
    try:
        # Calculate embeddings
        embedding = get_embeddings(skill.name)
        
        query = """
        CREATE (s:Skill {name: $name, skill_embedding: $embedding})
        RETURN id(s) as id, s.name as name
        """
        with driver.session() as session:
            result = session.run(query, name=skill.name, embedding=embedding)
            record = result.single()
            return SkillWithId(id=record["id"], name=record["name"])
    except Exception as e:
        logger.error(f"Error creating skill: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/core_competencies")
async def create_core_competency(competency: CoreCompetency) -> CoreCompetencyWithId:
    try:
        # Calculate embeddings
        embedding = get_embeddings(competency.name)
        
        query = """
        CREATE (cc:CoreCompetency {name: $name, core_competency_embedding: $embedding})
        RETURN id(cc) as id, cc.name as name
        """
        with driver.session() as session:
            result = session.run(query, name=competency.name, embedding=embedding)
            record = result.single()
            return CoreCompetencyWithId(id=record["id"], name=record["name"])
    except Exception as e:
        logger.error(f"Error creating core competency: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/skills/{skill_id}")
async def update_skill(skill_id: int, skill: Skill) -> SkillWithId:
    try:
        # Calculate new embeddings
        embedding = get_embeddings(skill.name)
        
        query = """
        MATCH (s:Skill)
        WHERE id(s) = $skill_id
        SET s.name = $name, s.skill_embedding = $embedding
        RETURN id(s) as id, s.name as name
        """
        with driver.session() as session:
            result = session.run(query, skill_id=skill_id, name=skill.name, embedding=embedding)
            record = result.single()
            if not record:
                raise HTTPException(status_code=404, detail="Skill not found")
            return SkillWithId(id=record["id"], name=record["name"])
    except Exception as e:
        logger.error(f"Error updating skill: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/core_competencies/{competency_id}")
async def update_core_competency(competency_id: int, competency: CoreCompetency) -> CoreCompetencyWithId:
    try:
        # Calculate new embeddings
        embedding = get_embeddings(competency.name)
        
        query = """
        MATCH (cc:CoreCompetency)
        WHERE id(cc) = $competency_id
        SET cc.name = $name, cc.core_competency_embedding = $embedding
        RETURN id(cc) as id, cc.name as name
        """
        with driver.session() as session:
            result = session.run(query, competency_id=competency_id, name=competency.name, embedding=embedding)
            record = result.single()
            if not record:
                raise HTTPException(status_code=404, detail="Core competency not found")
            return CoreCompetencyWithId(id=record["id"], name=record["name"])
    except Exception as e:
        logger.error(f"Error updating core competency: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/accomplishment/{accomplishment_id}", 
         response_model=Accomplishment,
         summary="Update an accomplishment",
         description="Update an accomplishment's name and body, and recalculate its embeddings")
async def update_accomplishment(
    accomplishment_id: int = Path(..., description="The ID of the accomplishment to update"),
    accomplishment: AccomplishmentUpdate = None
) -> Accomplishment:
    """
    Update an accomplishment and recalculate its embeddings.
    
    Parameters:
    - accomplishment_id: The ID of the accomplishment to update
    - accomplishment: The new accomplishment data
    
    Returns:
    - Updated accomplishment with its ID
    """
    try:
        # Calculate new embeddings for the accomplishment body
        embedding = get_embeddings(accomplishment.body)
        
        # Update the accomplishment in Neo4j
        query = """
        MATCH (acc:Accomplishment)
        WHERE id(acc) = $accomplishment_id
        SET acc.name = $name,
            acc.body = $body,
            acc.accomplishment_embedding = $embedding
        RETURN id(acc) as id, acc.name as name, acc.body as body
        """
        
        with driver.session() as session:
            result = session.run(
                query,
                accomplishment_id=accomplishment_id,
                name=accomplishment.name,
                body=accomplishment.body,
                embedding=embedding
            )
            record = result.single()
            
            if not record:
                raise HTTPException(status_code=404, detail="Accomplishment not found")
                
            return Accomplishment(
                id=record["id"],
                name=record["name"],
                body=record["body"]
            )
            
    except Exception as e:
        logger.error(f"Error updating accomplishment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/experiences",
         response_model=List[Experience],
         summary="Get all experiences",
         description="Retrieve all experience nodes from the database")
async def get_experiences() -> List[Experience]:
    """
    Get all experiences from the database.
    
    Returns:
    - List of experiences with their IDs, names, and companies
    """
    query = """
    MATCH (exp:Experience)
    RETURN id(exp) as id, exp.name as name, exp.company as company
    ORDER BY exp.company, exp.name
    """
    try:
        with driver.session() as session:
            result = session.run(query)
            return [Experience(id=record["id"], 
                             name=record["name"], 
                             company=record["company"]) 
                   for record in result]
    except Exception as e:
        logger.error(f"Error getting experiences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accomplishment",
          response_model=Accomplishment,
          summary="Create a new accomplishment",
          description="Create a new accomplishment node and link it to an experience")
async def create_accomplishment(accomplishment: CreateAccomplishment) -> Accomplishment:
    """
    Create a new accomplishment and link it to an experience.
    
    Parameters:
    - accomplishment: CreateAccomplishment object containing name, body, and experience_id
    
    Returns:
    - Created accomplishment with its ID
    """
    try:
        # Calculate embeddings for the accomplishment body
        embedding = get_embeddings(accomplishment.body)
        
        # Create the accomplishment and relationship in a single transaction
        query = """
        MATCH (exp:Experience)
        WHERE id(exp) = $experience_id
        CREATE (acc:Accomplishment {
            name: $name,
            body: $body,
            accomplishment_embedding: $embedding
        })
        CREATE (acc)<-[:ACHIEVED]-(exp)
        RETURN id(acc) as id, acc.name as name, acc.body as body
        """
        
        with driver.session() as session:
            result = session.run(
                query,
                experience_id=accomplishment.experience_id,
                name=accomplishment.name,
                body=accomplishment.body,
                embedding=embedding
            )
            record = result.single()
            
            if not record:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Experience with id {accomplishment.experience_id} not found"
                )
                
            return Accomplishment(
                id=record["id"],
                name=record["name"],
                body=record["body"]
            )
            
    except Exception as e:
        logger.error(f"Error creating accomplishment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
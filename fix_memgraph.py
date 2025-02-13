from neo4j import GraphDatabase
import logging
from collections import defaultdict
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_memgraph():
    """Connect to Memgraph database using Neo4j driver"""
    try:
        driver = GraphDatabase.driver("bolt://localhost:7687")
        logger.info("Successfully connected to Memgraph")
        return driver
    except Exception as e:
        logger.error(f"Failed to connect to Memgraph: {str(e)}")
        raise

def get_duplicates(driver, label: str) -> Dict[str, List[int]]:
    """
    Get duplicate nodes by name for a given label.
    Returns a dictionary where key is the name and value is a list of node IDs.
    Only includes names that have multiple IDs.
    """
    query = f"""
    MATCH (n:{label})
    RETURN id(n) as node_id, n.name as name
    ORDER BY n.name, id(n)
    """
    
    duplicates = defaultdict(list)
    try:
        with driver.session() as session:
            results = session.run(query)
            for record in results:
                duplicates[record['name']].append(record['node_id'])
        
        # Filter to only keep names with multiple IDs
        return {name: ids for name, ids in duplicates.items() if len(ids) > 1}
    except Exception as e:
        logger.error(f"Error getting duplicates for {label}: {str(e)}")
        raise

def fix_relationships(driver, name: str, keep_id: int, delete_ids: List[int], 
                     node_label: str, rel_type: str) -> None:
    """
    Fix relationships for duplicate nodes:
    1. Find all relationships of type rel_type pointing to nodes that will be deleted
    2. Create new relationships to the node we're keeping
    3. Delete the duplicate nodes
    """
    try:
        # Log what we're about to do
        logger.info(f"Fixing relationships for {node_label} '{name}'")
        logger.info(f"Keeping node ID {keep_id}, removing IDs {delete_ids}")
        
        with driver.session() as session:
            for delete_id in delete_ids:
                # Find and recreate relationships
                query = f"""
                MATCH (acc:Accomplishment)-[r:{rel_type}]->(n:{node_label})
                WHERE id(n) = $delete_id
                WITH acc, n
                MATCH (keep:{node_label})
                WHERE id(keep) = $keep_id
                MERGE (acc)-[:{rel_type}]->(keep)
                WITH acc, n
                MATCH (acc)-[r:{rel_type}]->(n)
                DELETE r
                """
                session.run(query, delete_id=delete_id, keep_id=keep_id)
                logger.info(f"Transferred relationships from node {delete_id} to {keep_id}")
                
                # Delete the duplicate node
                delete_query = f"""
                MATCH (n:{node_label})
                WHERE id(n) = $delete_id
                DELETE n
                """
                session.run(delete_query, delete_id=delete_id)
                logger.info(f"Deleted duplicate node {delete_id}")
            
    except Exception as e:
        logger.error(f"Error fixing relationships for {node_label} '{name}': {str(e)}")
        raise

def fix_duplicates(driver, label: str, relationship_type: str) -> None:
    """Fix duplicates for a given node label and relationship type"""
    logger.info(f"Starting to fix duplicates for {label} nodes")
    
    try:
        duplicates = get_duplicates(driver, label)
        logger.info(f"Found {len(duplicates)} {label} nodes with duplicates")
        
        for name, ids in duplicates.items():
            keep_id = ids[0]  # Keep the one with lowest ID
            delete_ids = ids[1:]  # Remove the rest
            fix_relationships(driver, name, keep_id, delete_ids, label, relationship_type)
            
        logger.info(f"Completed fixing duplicates for {label} nodes")
    except Exception as e:
        logger.error(f"Error in fix_duplicates for {label}: {str(e)}")
        raise

def main():
    try:
        driver = connect_to_memgraph()
        
        # Fix Skills
        fix_duplicates(driver, "Skill", "USED")
        
        # Fix Core Competencies
        fix_duplicates(driver, "CoreCompetency", "DEMONSTRATED")
        
        logger.info("Successfully completed fixing all duplicates")
        
        # Close the driver connection
        driver.close()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
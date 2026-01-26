import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Neo4jConnection:
    _driver = None
    _is_local = False
    
    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            # Try cloud Neo4j first
            uri = os.environ.get("NEO4J_URI", "neo4j+s://c8fbc0d8.databases.neo4j.io")
            user = os.environ.get("NEO4J_USER", "neo4j")
            password = os.environ.get("NEO4J_PASSWORD", "")
            
            try:
                cls._driver = GraphDatabase.driver(uri, auth=(user, password))
                # Test connection
                with cls._driver.session() as session:
                    session.run("RETURN 1")
                logger.info(f"Connected to Neo4j at {uri}")
                cls._is_local = False
            except Exception as e:
                logger.warning(f"Failed to connect to cloud Neo4j: {e}")
                # Fallback to local Neo4j
                try:
                    local_uri = "bolt://localhost:7687"
                    cls._driver = GraphDatabase.driver(local_uri, auth=("neo4j", "password"))
                    with cls._driver.session() as session:
                        session.run("RETURN 1")
                    logger.info("Connected to local Neo4j")
                    cls._is_local = True
                except Exception as e2:
                    logger.error(f"Failed to connect to local Neo4j: {e2}")
                    cls._driver = None
        return cls._driver
    
    @classmethod
    def close(cls):
        if cls._driver:
            cls._driver.close()
            cls._driver = None
    
    @classmethod
    def is_local(cls):
        return cls._is_local


def get_neo4j_session():
    driver = Neo4jConnection.get_driver()
    if driver:
        session = driver.session()
        try:
            yield session
        finally:
            session.close()
    else:
        yield None

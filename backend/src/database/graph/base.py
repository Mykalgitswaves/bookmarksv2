from neo4j import GraphDatabase
from src.config.config import settings

class Neo4jGraphDatabase:
    def __init__(self):
        self._driver = GraphDatabase.driver(
            settings.NEO4J_URI, 
            auth=(settings.NEO4J_USERNAME, 
                  settings.NEO4J_PASSWORD)
                  )

    def close(self):
        self._driver.close()

graph_db = Neo4jGraphDatabase()
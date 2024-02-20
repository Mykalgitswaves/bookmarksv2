from src.database.graph.base import GraphDatabase

class BaseCRUDRepositoryGraph:
    def __init__(self, driver: GraphDatabase):
        self.driver = driver._driver
        
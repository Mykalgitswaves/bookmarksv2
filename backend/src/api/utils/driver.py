import typing

from neo4j import GraphDatabase
from src.database.graph.base import graph_db

async def get_driver():
    try:
        yield graph_db
    except Exception as e:
        raise e
        
from pydantic import BaseSettings
from typing import List
import json

class Config(BaseSettings):
    #Uvicorn Configs
    HOST: str = "localhost"
    PORT: int
    API_PREFIX: str
    RELOAD: bool = True

    KEY_PAIR_NAME: str

    #Neo4j Configs
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    NEO4J_URI: str

    #Auth Configs
    JWT_SECRET_KEY: str
    JWT_ALGORITHM : str
    JWT_SCHEMES: List[str]
    JWT_MIN_EXPIRE: int
    JWT_SUBJECT: str

    #Google Books API Key
    GOOGLE_BOOKS_API_KEY: str

    #ADMIN CREDENTIALS
    ADMIN_CREDENTIALS: str


try:
    with open("src/config/config.json", "r") as file:
        config = json.load(file)
except:
    with open("../src/config/config.json", "r") as file:
        config = json.load(file)
settings = Config(**config)
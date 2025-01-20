from pydantic import BaseSettings
from typing import List
import json
import os

class Config(BaseSettings):
    #Uvicorn Configs
    HOST: str
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

    #WEB SOCKET Configs
    WS_SECRET_KEY: str
    WS_ALGORITHM : str
    WS_SCHEMES: List[str]
    WS_MIN_EXPIRE: int
    WS_SUBJECT: str

    #Google Books API Key
    GOOGLE_BOOKS_API_KEY: str

    #ADMIN CREDENTIALS
    ADMIN_CREDENTIALS: str

    #CORS Configs
    ALLOWED_ORIGINS: List[str]
    IS_ALLOWED_CREDENTIALS: bool
    ALLOWED_METHODS: List[str]
    ALLOWED_HEADERS: List[str]

    #RDS Configs
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_DATABASE: str
    MYSQL_ECHO: bool

    #Text length configs
    XSMALL_TEXT_LENGTH: int
    SMALL_TEXT_LENGTH: int
    MEDIUM_TEXT_LENGTH: int
    LARGE_TEXT_LENGTH: int
    XLARGE_TEXT_LENGTH: int

    # Email Configs
    MAIL_USERNAME: str 
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: str
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

environment = os.getenv("ENVIRONMENT", "feature")

if environment.lower() == "prod":
    config_file_path = "src/config/config.prod.json"
elif environment.lower() == "dev":
    config_file_path = "src/config/config.dev.json"
else:
    config_file_path = "src/config/config.feature.json"

try:
    with open(config_file_path, "r") as file:
        config = json.load(file)
except:
    with open("../" + config_file_path, "r") as file:
        config = json.load(file)
settings = Config(**config)
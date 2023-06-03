from database.db_helpers import (
    User,
    Review,
    Book,
    Author,
    Genre,
    Tag,
    Neo4jDriver
)
from fastapi import FastAPI, HTTPException


"""
Connect to database
"""

app = FastAPI()

@app.get("/")
async def get_data():
    data = {"cashmoney": "cashmoeny"}
    return data

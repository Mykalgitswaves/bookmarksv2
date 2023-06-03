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
async def get_test_user_data():
    driver = Neo4jDriver()
    result = driver.pull_user_node(user_id=int(1010015))
    return result
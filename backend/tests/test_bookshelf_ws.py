import pytest
from httpx import AsyncClient
import requests
import json
import time
import asyncio
import websockets

@pytest.fixture(scope="class")
def setup_class(request):
    """
    Fixture that sets up the test class by loading configuration from 'config.json' file,
    and initializing the necessary attributes for the test class.

    Args:
        request: The pytest request object.
    """
    with open("config.json", "r") as file:
        config = json.load(file)

    request.cls.endpoint = "http://127.0.0.1:8000"
    request.cls.username = "testuser123_posts"
    request.cls.email = "testuser_posts@testemail.com"
    request.cls.password = "testpassword"

    request.cls.admin_credentials = config["ADMIN_CREDENTIALS"]

    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Set Content-Type to application/json
    data = {
        "username": request.cls.username,
        "email": request.cls.email,
        "password": request.cls.password,
    }
    response = requests.post(f"{request.cls.endpoint}/api/auth/signup", headers=headers, data=data)
    assert response.status_code == 200, "Creating Test User"

    request.cls.access_token = response.json()["access_token"]
    request.cls.token_type = response.json()["token_type"]
    request.cls.user_id = response.json()["user_id"]

    yield

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

@pytest.mark.usefixtures("setup_class")
class TestBookshelfWS:
    """
    Test class for Websocket operations on Bookshelves
    """
    def test_create_bookshelf(self):
        """
        Test case to create a bookshelf.
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }

        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"
        bookshelf_id = response.json()["bookshelf_id"]

        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"

        response = requests.delete(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/delete", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Deleting Bookshelf"

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """
        Test case to check the websocket connection to the bookshelf.
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }

        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"
        bookshelf_id = response.json()["bookshelf_id"]

        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"

        uri = f"ws://127.0.0.1:8000/api/bookshelves/ws/{bookshelf_id}?token={self.access_token}"
        async with websockets.connect(uri) as ws:
            assert ws.open, "Websocket Connection"
            response = await ws.recv()
            print(response)
            assert response
        

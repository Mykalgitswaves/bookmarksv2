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
    request.cls.username = "testuser123_shelves"
    request.cls.email = "testuser_shelves@testemail.com"
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

    request.cls.username_2 = "testuser123_shelves_2"
    request.cls.email_2 = "testuser_shelves_2@testemail.com"
    request.cls.password_2 = "testpassword"

    request.cls.admin_credentials = config["ADMIN_CREDENTIALS"]

    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Set Content-Type to application/json
    data = {
        "username": request.cls.username_2,
        "email": request.cls.email_2,
        "password": request.cls.password_2,
    }
    response = requests.post(f"{request.cls.endpoint}/api/auth/signup", headers=headers, data=data)
    assert response.status_code == 200, "Creating Test User"

    request.cls.access_token_2 = response.json()["access_token"]
    request.cls.token_type_2 = response.json()["token_type"]
    request.cls.user_id_2 = response.json()["user_id"]

    yield

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username_2, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

@pytest.mark.usefixtures("setup_class")
class TestBookshelfMandatory:
    """
    Test class for Mandatory bookshelves
    """
    def test_get_bookshelves(self):
        """
        Test case to check the get endpoints for the mandatory shelves
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}  # Set Authorization header
        response = requests.get(f"{self.endpoint}/api/bookshelves/want_to_read/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Want to Read Shelf"
        print(response.json())
        bookshelf_id = response.json()["bookshelf"]["id"]

        # Test with the bookshelf_id endpoint
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Get Want to Read Shelf by ID"

        response = requests.get(f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Currently Reading Shelf"
        bookshelf_id = response.json()["bookshelf"]["id"]

        # Test with the bookshelf_id endpoint
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Get Currently Reading Shelf by ID"

        response = requests.get(f"{self.endpoint}/api/bookshelves/finished_reading/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Finished Reading Shelf"
        bookshelf_id = response.json()["bookshelf"]["id"]

        # Test with the bookshelf_id endpoint
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Get Finished Reading Shelf by ID"

    def test_bookshelf_previews(self):
        """
        Test case to check the get preview endpoints for the mandatory shelves
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        response = requests.get(f"{self.endpoint}/api/bookshelves/want_to_read/{self.user_id}/preview", headers=headers)
        assert response.status_code == 200, "Get Want to Read Shelf Preview"
        print(response.json())

        response = requests.get(f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}/preview", headers=headers)
        assert response.status_code == 200, "Get Currently Reading Shelf Preview"
        print(response.json())

        response = requests.get(f"{self.endpoint}/api/bookshelves/finished_reading/{self.user_id}/preview", headers=headers)
        assert response.status_code == 200, "Get Finished Reading Shelf Preview"
        print(response.json())

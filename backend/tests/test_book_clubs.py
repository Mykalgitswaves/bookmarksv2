import pytest
from httpx import AsyncClient
import requests
import json
import time

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
    request.cls.username = "testuser123_clubs"
    request.cls.email = "testuser_clubs@testemail.com"
    request.cls.password = "testPassword1!"

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

    request.cls.username_2 = "test_user123_clubs_2"
    request.cls.email_2 = "testuser_clubs_2@testemail.com"
    request.cls.password_2 = "testPassword1!"

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
class TestBookClubs:
    """
    Test class for bookclubs
    """
    @classmethod
    def setup_class(cls):
        cls.book_club_id = None  # Initialize book_club_id

    def test_create_bookclub(self):
        """
        Test case to check the create bookclub endpoint
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}  # Set Authorization header

        data = {
            "user_id": self.user_id,
            "name": "Test Book Club",
            "description": "This is a test book club",
            "book_club_pace": {
                "num_books": 1,
                "num_time_period": 1,
                "time_period": "weeks"
            }
        }

        response = requests.post(f"{self.endpoint}/api/bookclubs/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Book Club"
        print(response.json())
        ## Save book_club_id for future tests
        self.__class__.book_club_id = response.json()["book_club_id"]

    def test_search_users_not_in_club(self):
        """
        Test case to check the search users not in club endpoint
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        response = requests.get(f"{self.endpoint}/api/bookclubs/{self.book_club_id}/search/users/test", headers=headers)

        assert response.status_code == 200, "Searching Users Not In Club"
        print(response.json())

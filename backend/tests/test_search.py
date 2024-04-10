import requests
import json
import pytest
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
    request.cls.username = "testuser123"
    request.cls.email = "testuser@testemail.com"
    request.cls.password = "testpassword"
    request.cls.search_term = "fiction"

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


@pytest.mark.usefixtures("setup_class")
class TestSearch:
    def test_search_all(self):
        """
        Test case to verify search works across genre titles in the DB

        Returns:
            None
        """
        response = requests.get(f"{self.endpoint}/api/search/{self.search_term}?skip=0&limit=3")
        print(response.json())
        assert response.status_code == 200, "Search genres failed"
        assert len(response.json()) > 0, "Search genres failed"

    def test_search_users(self):
        """
        Test case to verify search works across users in the DB

        Returns:
            None
        """
        search_term = "test"
        headers = {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

        response = requests.get(f"{self.endpoint}/api/search/users/{search_term}?skip=0&limit=3",
                                headers=headers)
        print(response.json())
        assert response.status_code == 200, "Search users failed"
        assert len(response.json()) > 0, "Search users failed"

        
        
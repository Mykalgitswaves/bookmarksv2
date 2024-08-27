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
    request.cls.password = "testPassword1!"
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

    request.cls.username_friend = "friend_user123"
    request.cls.email_friend = "frienduser@testemail.com"
    request.cls.password_friend = "testPassword!1"
    request.cls.full_name_friend = "Friend User"
    
    data = {
        "username": request.cls.username_friend,
        "email": request.cls.email_friend,
        "password": request.cls.password_friend,
    }
    response = requests.post(f"{request.cls.endpoint}/api/auth/signup", headers=headers, data=data)
    assert response.status_code == 200, "Testing Signup Form"

    request.cls.access_token_friend = response.json()["access_token"]
    request.cls.token_type_friend = response.json()["token_type"]
    request.cls.user_id_friend = response.json()["user_id"]

    yield

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username",
                                json={"username": request.cls.username_friend, "admin_credentials": config["ADMIN_CREDENTIALS"]})
    
    assert response.status_code == 200, "Cleanup: Test user deletion failed"

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
        search_term = "friend_user123"
        headers = {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

        response = requests.get(f"{self.endpoint}/api/search/users/{search_term}?skip=0&limit=3",
                                headers=headers)
        print(response.json())
        assert response.status_code == 200, "Search users failed"
        assert len(response.json()['data']) > 0, "Search users failed"

    def test_search_friends(self):
        """
        Test case to verify search works across friends in the DB

        Returns:
            None
        """

        headers = {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

        friend_headers = {
            "Authorization": f"{self.token_type_friend} {self.access_token_friend}"
        }

        response = requests.put(f"{self.endpoint}/api/user/{self.user_id_friend}/send_friend_request", headers=headers)
        assert response.status_code == 200, "Testing Send Friend Request"

        response = requests.put(f"{self.endpoint}/api/user/{self.user_id}/accept_friend_request", headers=friend_headers)
        assert response.status_code == 200, "Testing Accept Friend Request"


        search_term = "friend_user123"

        response = requests.get(f"{self.endpoint}/api/search/friends/{search_term}?skip=0&limit=3",
                                headers=headers)
        print(response.json())
        assert response.status_code == 200, "Search friends failed"
        assert len(response.json()['data']) > 0, "Search friends failed"

        search_term = "test"

        response = requests.get(f"{self.endpoint}/api/search/friends/{search_term}?skip=0&limit=3",
                                headers=headers)
        print(response.json())
        # This should return an empty list as no friends with the search term exist
        assert response.status_code == 200, "Search friends failed"
        assert len(response.json()['data']) == 0, "Search friends failed"

        
        
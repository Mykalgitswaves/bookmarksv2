import requests
import json
import pytest

@pytest.fixture(scope="class")
def setup_class(request):
    """
    Fixture that sets up the test class by creating a test user and obtaining an access token.
    It also cleans up by deleting the test user after the tests are executed.
    """
    with open("config.json", "r") as file:
        config = json.load(file)

    request.cls.endpoint = "http://127.0.0.1:8000"
    request.cls.username = "testuser123"
    request.cls.email = "testuser@testemail.com"
    request.cls.password = "testpassworD1!"
    request.cls.full_name = "Test User"
    request.cls.genres = ["76667bea-1e4c-4928-9718-ad498f4c1fc2","348af800-1ccc-4885-b80a-ca0f3e0de508"]
    request.cls.authors = ["1","2"]
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Set Content-Type to application/json
    data = {
        "username": request.cls.username,
        "email": request.cls.email,
        "password": request.cls.password,
    }
    response = requests.post(f"{request.cls.endpoint}/api/auth/signup", headers=headers, data=data)
    assert response.status_code == 200, "Testing Signup Form"

    request.cls.access_token = response.json()["access_token"]
    request.cls.token_type = response.json()["token_type"]

    yield

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

@pytest.mark.usefixtures("setup_class")
class TestSetupUser:
    """
    Test class for setting up user properties such as full name, genres, and authors.
    """

    def test_set_full_name(self):
        """
        Test case for setting the full name of the user.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        # Prepare the data to be sent in the request body
        data = {
            "full_name": self.full_name
        }
        
        # Send a PUT request to set the full name of the user
        response = requests.put(f"{self.endpoint}/api/setup-user/full_name", headers=headers, json=data)
        
        # Assert that the response status code is 200
        assert response.status_code == 200, "Testing Set Full Name"
        
        # Send a GET request to retrieve the user properties
        user_response = requests.get(f"{self.endpoint}/api/user/me", headers=headers)
        
        # Assert that the response status code is 200
        assert user_response.status_code == 200, "Failed to get user properties"
        
        # Print the user response JSON
        print(user_response.json())
        
        # Assert that the user full name is set correctly
        assert "full_name" in user_response.json(), "Failed to get user full name"
        assert user_response.json()["full_name"] == self.full_name, "Failed to set user full name"

    def test_set_genres(self):
        """
        Test case for setting the genres liked by the user.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        # Prepare the data to be sent in the request body
        data = {
            "genres": self.genres
        }
        
        # Send a PUT request to set the genres liked by the user
        response = requests.put(f"{self.endpoint}/api/setup-user/genres", headers=headers, json=data)
        
        # Assert that the response status code is 200
        assert response.status_code == 200, "Testing Set Genres"

        # Send a GET request to retrieve the user liked genres
        genres = requests.get(f"{self.endpoint}/api/user/me/liked_genres", headers=headers)
        
        # Assert that the response status code is 200
        assert genres.status_code == 200, "Failed to get user liked genres"
        
        # Assert that the user liked genres are set correctly
        assert set(self.genres).issubset(genres.json()["liked_genres"]), "Failed to set user liked genres"

    def test_set_authors(self):
        """
        Test case for setting the authors liked by the user.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        # Prepare the data to be sent in the request body
        data = {
            "authors": self.authors
        }
        
        # Send a PUT request to set the authors liked by the user
        response = requests.put(f"{self.endpoint}/api/setup-user/authors", headers=headers, json=data)
        
        # Assert that the response status code is 200
        assert response.status_code == 200, "Testing Set Authors"

        # Send a GET request to retrieve the user liked authors
        author_response = requests.get(f"{self.endpoint}/api/user/me/liked_authors", headers=headers)
        
        # Assert that the response status code is 200
        assert author_response.status_code == 200, "Failed to get user liked authors"
        
        # Assert that the user liked authors are set correctly
        assert set(self.authors).issubset(author_response.json()["liked_authors"]), "Failed to set user liked authors"

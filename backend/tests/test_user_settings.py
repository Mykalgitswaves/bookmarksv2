import requests
import json
import pytest
import time

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
    request.cls.password = "testPassword1!"
    request.cls.full_name = "Test User"
    request.cls.genres = ["76667bea-1e4c-4928-9718-ad498f4c1fc2","348af800-1ccc-4885-b80a-ca0f3e0de508"]
    request.cls.authors = ["1","2"]
    request.cls.new_username = "newusername"
    
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
    request.cls.user_id = response.json()["user_id"]

    yield

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.new_username, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

@pytest.mark.usefixtures("setup_class")
class TestUserSettings:
    """
    Test class for altering user settings.
    """

    def test_get_settings(self):
        """
        Test case for setting the full name of the user.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        # Send a GET request to get the settings of the user
        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/get_user", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Testing Get User Settings"

    def test_update_bio(self):
        """
        Test case for updating the bio of the user.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        # Send a PUT request to update the bio of the user
        response = requests.put(f"{self.endpoint}/api/user/{self.user_id}/update_bio", headers=headers, json="This is a test bio.")
        assert response.status_code == 200, "Testing Update bio"
        
        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/get_user", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Testing Get User Settings"
        assert response.json()["data"]["bio"] == "This is a test bio.", "Testing Bio Update"

    def test_update_email(self):
        """
        Test case for updating the bio of the user.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        # Send a PUT request to update the email of the user
        response = requests.put(f"{self.endpoint}/api/user/{self.user_id}/update_email", headers=headers, json="test_email@test.com")
        print(response.json())
        assert response.status_code == 200, "Testing Update email"
        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/get_user", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Testing Get User Settings"
        assert response.json()["data"]["email"] == "test_email@test.com", "Testing email Update"

    def test_update_profile_img_url(self):
        """
        Test case for updating the bio of the user.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        # Send a PUT request to update the profile_img_url of the user
        response = requests.put(f"{self.endpoint}/api/user/{self.user_id}/update_profile_img", headers=headers, json={"cdn_url":"www.imagecrab.com/test_image.jpg"})
        print(response.json())
        assert response.status_code == 200, "Testing Update profile_img_url"
        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/get_user", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Testing Get User Settings"
        assert response.json()["data"]["profile_img_url"] == "www.imagecrab.com/test_image.jpg", "Testing profile_img_url Update"

    def test_update_password(self):
        """
        Test case for updating the bio of the user.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        # Send a PUT request to update the password of the user
        response = requests.put(f"{self.endpoint}/api/user/{self.user_id}/update_password", headers=headers, json="NewPassword123!")
        print(response.json())
        assert response.status_code == 200, "Testing Update password"

    def test_update_username(self):
        """
        Test case for updating the username of the user.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        # Send a PUT request to update the username of the user
        response = requests.put(f"{self.endpoint}/api/user/{self.user_id}/update_username", headers=headers, json=self.new_username)
        assert response.status_code == 200, "Testing Update Username"
        access_token = response.json()["access_token"]
        token_type = response.json()["token_type"]
        print(response.json())
        # Send a GET request to get the settings of the user
        headers = {"Authorization": f"{token_type} {access_token}"}

        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/get_user", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Testing Get User Settings"
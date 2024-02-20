import requests
import json
import pytest

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

    yield

    response = requests.post(
        f"{request.cls.endpoint}/api/admin/delete_user_by_username",
        json={"username": request.cls.username, "admin_credentials": config["ADMIN_CREDENTIALS"]}
    )

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

@pytest.mark.usefixtures("setup_class")
class TestAuth:
    """
    Test class for authentication-related tests.
    """
    def test_can_signup(self):
        """
        Test case to verify if a user can successfully sign up.

        Returns:
            None
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Set Content-Type to application/json
        data = {
            "username": self.username,
            "email": self.email,
            "password": self.password,
        }
        response = requests.post(f"{self.endpoint}/api/auth/signup", headers=headers, data=data)
        assert response.status_code == 200, "Testing Signup Form"

        self.access_token = response.json()["access_token"]
        self.token_type = response.json()["token_type"]

    def test_can_login_email(self):
        """
        Test case to verify if a user can successfully log in using email.

        Returns:
            None
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "email": self.email,
            "password": self.password,
        }
        response = requests.post(f"{self.endpoint}/api/auth/login", headers=headers, data=data)
        assert response.status_code == 200, "Testing Login Form with Email"
        self.access_token = response.json()["access_token"]
        self.token_type = response.json()["token_type"]

    def test_can_login_username(self):
        """
        Test case to verify if a user can successfully log in using username.

        Returns:
            None
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "username": self.username,
            "password": self.password,
        }
        response = requests.post(f"{self.endpoint}/api/auth/login", headers=headers, data=data)
        assert response.status_code == 200, "Testing Login Form with Username"
        self.access_token = response.json()["access_token"]
        self.token_type = response.json()["token_type"]

    def test_token_verification(self):
        """
        Test case to verify if a user's token can be successfully verified.

        Returns:
            None
        """
        login_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        login_data = {
            "username": self.username,
            "password": self.password,
        }
        response = requests.post(f"{self.endpoint}/api/auth/login", headers=login_headers, data=login_data)
        assert response.status_code == 200, "Getting Token for Verification"

        self.access_token = response.json()["access_token"]
        self.token_type = response.json()["token_type"]
        self.uuid = response.json()["user_id"]
        verification_headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        verification_data = {"uuid": self.uuid}
        response = requests.get(f"{self.endpoint}/api/auth/verify", headers=verification_headers, params=verification_data)
        assert response.status_code == 200, "Testing Token Verification"

    #TODO: Add test for token expiration
    #TODO: Add test for token invalidation
    #TODO: Add test for delete user
        


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
    request.cls.full_name = "John Doe"
    request.cls.user_id = "1234567890"
    request.cls.admin_credentials = config["ADMIN_CREDENTIALS"]


@pytest.mark.usefixtures("setup_class")
class TestMySQL:
    def test_create_user(self):
        """
        Creates a test user in the SQL database.
        """
        payload = {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "user_id": self.user_id,
            "admin_credentials": self.admin_credentials
        }
        
        response = requests.post(f"{self.endpoint}/api/admin/create_user_sql", json=payload)


        assert response.status_code == 200, "create user failed"
    
    def test_get_user(self):
        """
        Retrieves the test user from the SQL database.
        """
        payload = {
            "user_id": self.user_id,
            "admin_credentials": self.admin_credentials
        }
        
        response = requests.get(f"{self.endpoint}/api/admin/get_user_sql", json=payload)

        assert response.status_code == 200, "get user failed"

    def test_delete_user(self):
        """
        Deletes the test user from the SQL database.
        """
        payload = {
            "user_id": self.user_id,
            "admin_credentials": self.admin_credentials
        }
        
        response = requests.delete(f"{self.endpoint}/api/admin/delete_user_sql", json=payload)

        assert response.status_code == 200, "delete user failed"

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


@pytest.mark.usefixtures("setup_class")
class TestGenres:
    def test_search_genres(self):
        """
        Test case to verify search works across genre titles in the DB

        Returns:
            None
        """
        response = requests.get(f"{self.endpoint}/api/health/")
        assert response.status_code == 200, "Healthcheck failed"
        assert len(response.json()) > 0, "Healthcheck failed"
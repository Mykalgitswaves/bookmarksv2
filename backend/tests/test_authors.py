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
    request.cls.search_term = "scott"

    request.cls.author_id = "247"
    request.cls.author_name = "Isaac Asimov"
    request.cls.author_book_id = "ceb2edf98-7176-4b60-8740-34e9dff53406"


@pytest.mark.usefixtures("setup_class")
class TestAuthors:
    def test_search_authors(self):
        """
        Test case to verify search works across author titles in the DB

        Returns:
            None
        """
        response = requests.get(f"{self.endpoint}/api/authors/search/{self.search_term}?skip=0&limit=3")
        print(response.json())
        assert response.status_code == 200, "Search authors failed"
        assert len(response.json()) > 0, "Search authors failed"
    
    def test_author_by_id(self):
        """
        Test case to get an author page
        """

        response = requests.get(f"{self.endpoint}/api/authors/{self.author_id}")
        print(response.json()['author'])
        assert response.status_code == 200, "Get author by id failed"
        
        assert response.json()["author"]["id"] == self.author_id, "Get author by id failed"
        assert response.json()["author"]["name"] == self.author_name, "Get author by id- name failed"
        assert any(book['id'] == self.author_book_id for book in response.json()["author"]["books"]), "Get author by id- books failed"
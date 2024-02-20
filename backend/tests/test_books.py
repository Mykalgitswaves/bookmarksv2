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
    request.cls.search_term = "Foundation"
    request.cls.book_id_in_db = "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872"
    request.cls.google_book_id_in_db = "g_uawAAAAIAAJ"
    request.cls.google_book_id_not_in_db = "gyooFEAAAQBAJ"
    request.cls.google_book_id_not_in_db_title = "Dr. Seuss's Oh, the Places You'll Go! Coloring Book"
    request.cls.google_book_id_not_in_db_with_versions = "gHIp_0N3uPPcC"
    request.cls.google_book_id_not_in_db_with_versions_title = "The Historical Jesus in Context"
    request.cls.google_book_id_not_in_db_with_versions_version_id = "gwMbEyeDSQQgC"

    yield
    time.sleep(5)
    response = requests.post(
        f"{request.cls.endpoint}/api/admin/delete_book_and_versions_by_google_id",
        json={"google_id": request.cls.google_book_id_not_in_db, "admin_credentials": config["ADMIN_CREDENTIALS"]}
    )

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

    response = requests.post(
        f"{request.cls.endpoint}/api/admin/delete_book_and_versions_by_google_id",
        json={"google_id": request.cls.google_book_id_not_in_db_with_versions, "admin_credentials": config["ADMIN_CREDENTIALS"]}
    )

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

@pytest.mark.usefixtures("setup_class")
class TestBooks:
    """
    Test class for authentication-related tests.
    """
    def test_search_books(self):
        """
        Test case to verify search works across book titles in the DB

        Returns:
            None
        """
        
        response = requests.get(f"{self.endpoint}/api/books/search/{self.search_term}?skip=0&limit=3")
        assert response.status_code == 200, "Testing books search"
        
        assert len(response.json()["data"]) > 0, "Testing books search"

    def test_get_book_by_id(self):
        """
        Test case to verify book by id works

        Returns:
            None
        """
        # Testing a book in the database
        response = requests.get(f"{self.endpoint}/api/books/{self.book_id_in_db}")
        assert response.status_code == 200, "Testing book by id"
        print(response.json())
        assert response.json()["data"]["id"] == self.book_id_in_db, "Testing book by id"

    def test_get_book_by_google_id(self):
        """
        Test case to verify book by id works

        Returns:
            None
        """
        # Testing a book in the database
        response = requests.get(f"{self.endpoint}/api/books/{self.google_book_id_in_db}")
        assert response.status_code == 200, "Testing book by google id"
        print(response.json())
        assert response.json()["data"]["google_id"] == self.google_book_id_in_db, "Testing book by google id"
        assert response.json()["data"]["id"] == self.book_id_in_db, "Testing book by id"

    def test_get_book_by_google_id_not_in_db(self):
        """
        Test case to verify book by google id works when the book is not in the DB
        """
        response = requests.get(f"{self.endpoint}/api/books/{self.google_book_id_not_in_db}")
        assert response.status_code == 200, "Testing book by google id"
        print(response.json())
        assert response.json()["data"]["google_id"] == self.google_book_id_not_in_db, "Testing book by google id"
        assert response.json()["data"]["title"] == self.google_book_id_not_in_db_title, "Testing book by google id"

    def test_get_book_by_google_id_not_in_db_with_versions(self):
        """
        Test case to verify book by google id works when the book is not in the DB and pulls versions
        """
        response = requests.get(f"{self.endpoint}/api/books/{self.google_book_id_not_in_db_with_versions}")
        assert response.status_code == 200, "Testing book by google id"
        print(response.json())
        assert response.json()["data"]["google_id"] == self.google_book_id_not_in_db_with_versions, "Testing book by google id"
        assert response.json()["data"]["title"] == self.google_book_id_not_in_db_with_versions_title, "Testing book by google id"
        time.sleep(5)
        versions_response = requests.get(f"{self.endpoint}/api/books/{self.google_book_id_not_in_db_with_versions}/versions")
        print(versions_response.json())
        assert versions_response.status_code == 200, "Testing book versions by google id"
        assert len(versions_response.json()["data"]) > 0, "Testing book versions by google id"
        assert any(book['google_id'] == self.google_book_id_not_in_db_with_versions_version_id for book in versions_response.json()["data"]), "Correct version found"

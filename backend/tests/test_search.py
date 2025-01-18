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

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_book_club_data",
                                json={"user_id": request.cls.user_id, "admin_credentials": config["ADMIN_CREDENTIALS"]})
    
    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_bookshelf_data",
                            json={"user_id": request.cls.user_id, "admin_credentials": config["ADMIN_CREDENTIALS"]})

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

        response = requests.put(f"{self.endpoint}/api/user/{self.user_id}/send_friend_request/{self.user_id_friend}", headers=headers)
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

    def test_search_book_clubs(self):
        """
        Test case to verify search works across book clubs in the DB
        """

        headers = {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

        # Create a bookclub
        response = requests.post(
            f"{self.endpoint}/api/bookclubs/create", 
            headers=headers, 
            json={
                "name": "test book club",
                "description": "test description",
                "user_id": self.user_id
                })

        assert response.status_code == 200, "Creating Book Club"

        search_term = "test"

        response = requests.get(
            f"{self.endpoint}/api/search/bookclubs/{search_term}?skip=0&limit=3",
            headers=headers
        )

        print(response.json())
        assert response.status_code == 200, "Search book clubs failed"
        assert len(response.json()['data']) > 0, "Search book clubs failed"
        assert len(response.json()['data']) <= 3, "Search book clubs failed"
        
        headers = {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

        search_term = "test"

        response = requests.get(
            f"{self.endpoint}/api/search/bookclubs/{search_term}",
            headers=headers
        )

        print(response.json())
        assert response.status_code == 200, "Search book clubs failed"
        assert len(response.json()['data']) > 0, "Search book clubs failed"
        assert len(response.json()['data']) <= 5, "Search book clubs failed"

    def test_search_book_shelves(self):
        """
        Test case to verify search works across book clubs in the DB
        """

        headers = {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }

        # Send a POST request to create a bookshelf
        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"
        bookshelf_id = response.json()["bookshelf_id"]

        search_term = "test"

        response = requests.get(
            f"{self.endpoint}/api/search/bookshelves/{search_term}?skip=0&limit=3",
            headers=headers
        )

        print(response.json())
        assert response.status_code == 200, "Search bookshelf failed"
        assert len(response.json()['data']) > 0, "Search bookshelf failed"
        assert len(response.json()['data']) <= 3, "Search bookshelf failed"

        book_data_1 = {
            	"book" : {
                    "id" : "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872",
                    "author_names": ["Isaac Asimov"],
                    "title": "Foundation",
                    "small_img_url": "http://books.google.com/books/content?id=_uawAAAAIAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE732DLT-Q5P4M6ll9fpW5DH-Lz-FrGxwAQptgERj0vxnZYrLz57WvWzJ5k8Rr-OVQdQBOAImZNKuZQkgOgOO1HH2l5tUMj62Zngs0JbkXfsQIy3PcS_v8oHhB3XB7M0irmn4gM9g&source=gbs_api"
                }
        }


        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        response = requests.put(f"{self.endpoint}/api/bookshelves/quick_add/{bookshelf_id}", 
                                 json=book_data_1, headers=headers)
        assert response.status_code == 200, "Quick Add to Shelf"
        print(response.json(), "quick add want to read")
        
        headers = {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

        search_term = "test"

        response = requests.get(
            f"{self.endpoint}/api/search/bookshelves/{search_term}",
            headers=headers
        )

        print(response.json())
        assert response.status_code == 200, "Search book clubs failed"
        assert len(response.json()['data']) > 0, "Search book clubs failed"
        assert len(response.json()['data']) <= 5, "Search book clubs failed"


        
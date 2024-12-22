import pytest
import requests
import json
import time
from datetime import datetime, timezone
from bs4 import BeautifulSoup

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
    request.cls.username = "testuser123_clubs"
    request.cls.email = "testuser_clubs@testemail.com"
    request.cls.password = "testPassword1!"

    request.cls.admin_credentials = config["ADMIN_CREDENTIALS"]

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

    request.cls.username_2 = "test_user123_clubs_2"
    request.cls.email_2 = "testuser_clubs_2@testemail.com"
    request.cls.password_2 = "testPassword1!"

    request.cls.admin_credentials = config["ADMIN_CREDENTIALS"]

    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Set Content-Type to application/json
    data = {
        "username": request.cls.username_2,
        "email": request.cls.email_2,
        "password": request.cls.password_2,
    }
    response = requests.post(f"{request.cls.endpoint}/api/auth/signup", headers=headers, data=data)
    assert response.status_code == 200, "Creating Test User"

    request.cls.access_token_2 = response.json()["access_token"]
    request.cls.token_type_2 = response.json()["token_type"]
    request.cls.user_id_2 = response.json()["user_id"]

    request.cls.username_3 = "test_user133_clubs_3"
    request.cls.email_3 = "testuser_clubs_3@testemail.com"
    request.cls.password_3 = "testPassword1!"

    request.cls.admin_credentials = config["ADMIN_CREDENTIALS"]

    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Set Content-Type to application/json
    data = {
        "username": request.cls.username_3,
        "email": request.cls.email_3,
        "password": request.cls.password_3,
    }
    response = requests.post(f"{request.cls.endpoint}/api/auth/signup", headers=headers, data=data)
    assert response.status_code == 200, "Creating Test User"

    request.cls.access_token_3 = response.json()["access_token"]
    request.cls.token_type_3 = response.json()["token_type"]
    request.cls.user_id_3 = response.json()["user_id"]

    request.cls.username_4 = "test_user144_clubs_4"
    request.cls.email_4 = "testuser_clubs_4@testemail.com"
    request.cls.password_4 = "testPassword1!"

    request.cls.admin_credentials = config["ADMIN_CREDENTIALS"]

    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Set Content-Type to application/json
    data = {
        "username": request.cls.username_4,
        "email": request.cls.email_4,
        "password": request.cls.password_4,
    }
    response = requests.post(f"{request.cls.endpoint}/api/auth/signup", headers=headers, data=data)
    assert response.status_code == 200, "Creating Test User"

    request.cls.access_token_4 = response.json()["access_token"]
    request.cls.token_type_4 = response.json()["token_type"]
    request.cls.user_id_4 = response.json()["user_id"]

    yield

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_book_club_data", 
                             json={"user_id": request.cls.user_id, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test book club deletion failed"

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username_2, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username_3, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username_4, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

@pytest.mark.usefixtures("setup_class")
class TestBookClubs:
    """
    Test class for bookclubs
    """
    @classmethod
    def setup_class(cls):
        cls.book_club_id = None  # Initialize book_club_id
        cls.invite_id = None  # Initialize invite_id
        cls.invite_id_2 = None
        cls.post_id = None
        cls.award_id = None

    def test_create_bookclub(self):
        """
        Test case to check the create bookclub endpoint
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}  # Set Authorization header

        data = {
            "user_id": self.user_id,
            "name": "Test Book Club",
            "description": "This is a test book club",
            "book_club_pace": {
                "num_books": 1,
                "num_time_period": 1,
                "time_period": "weeks"
            }
        }

        response = requests.post(f"{self.endpoint}/api/bookclubs/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Book Club"
        print(response.json())
        ## Save book_club_id for future tests
        self.__class__.book_club_id = response.json()["book_club_id"]

    def test_search_users_not_in_club(self):
        """
        Test case to check the search users not in club endpoint
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        response = requests.get(f"{self.endpoint}/api/bookclubs/{self.book_club_id}/search/users/test", headers=headers)

        assert response.status_code == 200, "Searching Users Not In Club"
        print(response.json())
    
    def test_invite_users_to_club(self):
        """
        Test case to check the invite users to club endpoint
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "user_ids": [self.user_id_2],
            "emails": ["random_email@hardcoverlit.com"],
            "book_club_id": self.book_club_id
        }

        response = requests.post(f"{self.endpoint}/api/bookclubs/invite_legacy", headers=headers, json=data)

        print(response.json())
        assert response.status_code == 200, "Inviting Users to Club"

        data = {
            "user_ids": [],
            "emails": ["random_email_2@hardcoverlit.com"],
            "book_club_id": self.book_club_id
        }

        response = requests.post(f"{self.endpoint}/api/bookclubs/invite_legacy", headers=headers, json=data)

        print(response.json())
        assert response.status_code == 200, "Inviting Users to Club"

        data = {
            "user_ids": [self.user_id_3],
            "emails": [],
            "book_club_id": self.book_club_id
        }

        response = requests.post(f"{self.endpoint}/api/bookclubs/invite_legacy", headers=headers, json=data)

        print(response.json())
        assert response.status_code == 200, "Inviting Users to Club"

    def test_get_invites(self):
        """
        Test case to check the get invites endpoint
        """

        headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}

        response = requests.get(f"{self.endpoint}/api/bookclubs/invites/{self.user_id_2}", headers=headers)

        assert response.status_code == 200, "Getting Invites"
        print(response.json())
        assert len(response.json()['invites']) > 0, "No Invites Found"
        self.__class__.invite_id = response.json()['invites'][0]['invite_id']

        headers = {"Authorization": f"{self.token_type_3} {self.access_token_3}"}

        response = requests.get(f"{self.endpoint}/api/bookclubs/invites/{self.user_id_3}", headers=headers)

        assert response.status_code == 200, "Getting Invites"
        print(response.json())
        assert len(response.json()['invites']) > 0, "No Invites Found"
        self.__class__.invite_id_2 = response.json()['invites'][0]['invite_id']

    def test_decline_invite(self):
        """
        Test case to check the decline invite endpoint
        """

        headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}

        endpoint = f"{self.endpoint}/api/bookclubs/invites/decline/{self.invite_id}"

        response = requests.put(endpoint, headers=headers)

        assert response.status_code == 200, "Declining Invite"
        print(response.json())

    def test_accept_invite(self):
        """
        Test case to check the accept invite endpoint
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "user_ids": [self.user_id_2],
            "emails": ["hardcoverlit@gmail.com"],
            "book_club_id": self.book_club_id
        }

        response = requests.post(f"{self.endpoint}/api/bookclubs/invite_legacy", headers=headers, json=data)

        print(response.json())
        assert response.status_code == 200, "Inviting Users to Club"

        headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}

        response = requests.get(f"{self.endpoint}/api/bookclubs/invites/{self.user_id_2}", headers=headers)

        assert response.status_code == 200, "Getting Invites"
        print(response.json())
        assert len(response.json()['invites']) > 0, "No Invites Found"
        invite_id = response.json()['invites'][0]['invite_id']


        headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}

        endpoint = f"{self.endpoint}/api/bookclubs/invites/accept/{invite_id}"

        response = requests.put(endpoint, headers=headers)

        assert response.status_code == 200, "Accepting Invite"
        print(response.json())

    def test_new_send_invite(self):
        """
        Tests the new invite endpoint
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "invites" : { 
                0: {
                    "user_id": self.user_id_2
                },
                1: {
                    "user_id": self.user_id_3
                },
                2: {
                    "user_id": self.user_id_4
                },
                3: {
                    "email": "hardcoverlit@gmail.com"
                },
                4: {
                    "email": "hardcoverlitnew@gmail.com"
                },
                5: {
                    "email": "testuser_clubs_2@testemail.com"
                }
            },
            "book_club_id":self.book_club_id
        }

        response = requests.post(
            f"{self.endpoint}/api/bookclubs/invite", 
            headers=headers, 
            json=data)

        print(response.json())
        assert response.status_code == 200, "Inviting Users to Club"

    def test_get_owned_clubs(self):
        """
        Test case to check the get owned clubs endpoint
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        response = requests.get(f"{self.endpoint}/api/bookclubs/owned/{self.user_id}", headers=headers)

        assert response.status_code == 200, "Getting Owned Clubs"
        assert len(response.json()['bookclubs']) > 0, "No Owned Clubs Found"
        print(response.json())

        response = requests.get(f"{self.endpoint}/api/bookclubs/owned/{self.user_id}?limit=1", headers=headers)

        assert response.status_code == 200, "Getting Owned Clubs with limit"
        assert len(response.json()['bookclubs']) == 1, "Incorrect number of clubs returned"
        print(response.json())

    def test_get_member_clubs(self):
        """
        Test case to check the get member clubs endpoint
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        response = requests.get(f"{self.endpoint}/api/bookclubs/member/{self.user_id_2}", headers=headers)

        print(response.json())
        assert response.status_code == 200, "Getting Member Clubs"
        assert len(response.json()['bookclubs']) > 0, "No Member Clubs Found"

        response = requests.get(f"{self.endpoint}/api/bookclubs/member/{self.user_id_2}?limit=1", headers=headers)

        assert response.status_code == 200, "Getting Member Clubs with limit"
        assert len(response.json()['bookclubs']) == 1, "Incorrect number of clubs returned"
        print(response.json())

    def test_currently_reading_books(self):
        """
        Test case to check the currently reading book endpoints
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "expected_finish_date": datetime.now(timezone.utc).isoformat(),
            "book": {
                "id": "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872",
                "chapters": 10
            }
        }

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "currently_reading/start")

        response = requests.post(endpoint, json=data, headers=headers)
        assert response.status_code == 200, "Starting a currently reading book"

        # Test the currently reading book endpoint
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "currently_reading")

        response = requests.get(endpoint, headers=headers)
        assert response.status_code == 200, "Error getting currently reading book"
        book = response.json()['currently_reading_book']
        assert book is not None, "Book not set or returned"

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "currently_reading/stop")

        response = requests.post(endpoint, headers=headers)
        assert response.status_code == 200, "Stopping a currently reading book"

        # Test the currently reading book endpoint
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "currently_reading")

        response = requests.get(endpoint, headers=headers)
        assert response.status_code == 200, "Error getting currently reading book"
        book = response.json()['currently_reading_book']
        assert book is None, "Book still set"

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "currently_reading/start")

        response = requests.post(endpoint, json=data, headers=headers)
        assert response.status_code == 200, "Starting a currently reading book"

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "currently_reading/finish")

        response = requests.post(endpoint, headers=headers)
        assert response.status_code == 200, "Finishing a currently reading book"

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "currently_reading/start")

        response = requests.post(endpoint, json=data, headers=headers)
        assert response.status_code == 200, "Starting a currently reading book"

    def test_pace_endpoints(self):
        """
        Tests the pace related endpoints for owner and members
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        endpoint = (
                f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
                "user_pace")
        
        response = requests.get(endpoint, headers=headers)
        assert response.status_code == 200, "Getting user pace"

        headers_2 = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}
        
        response = requests.get(endpoint, headers=headers_2)
        assert response.status_code == 200, "Getting user pace"

        endpoint = (
                f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
                "club_members_pace")
        
        response = requests.get(endpoint, headers=headers)
        assert response.status_code == 200, "Getting club members pace"
        
        response = requests.get(endpoint, headers=headers_2)
        assert response.status_code == 200, "Getting club members pace"

    def test_create_update(self):
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "user":{
                "id": self.user_id
            },
            "chapter": 1,
            "response": "I am reading this book",
            "headline": "This is a headline",
            "quote": "This is a quote"      
        }
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "update/create")
        
        response = requests.post(endpoint, json=data, headers=headers)
        
        assert response.status_code == 200, "Creating an update"
        print(response.json())
        
        data = {
            "user":{
                "id": self.user_id
            },
            "chapter": 2,
            "response": "I am reading this book",
            "headline": "This is a headline",    
        }

        response = requests.post(endpoint, json=data, headers=headers)
        
        assert response.status_code == 200, "Creating an update"
        print(response.json())
        
        headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}
        data = {
            "user":{
                "id": self.user_id_2
            },
            "chapter": 7,
            "response": "I am reading this book",
        }
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "update/create")
        
        response = requests.post(endpoint, json=data, headers=headers)
        
        assert response.status_code == 200, "Creating an update"
        print(response.json())
        
        data = {
            "user":{
                "id": self.user_id_2
            },
            "chapter": 8
        }

        response = requests.post(endpoint, json=data, headers=headers)
        
        assert response.status_code == 200, "Creating an update"
        print(response.json())
        
    def test_get_feed(self):
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "feed")
        
        response = requests.get(endpoint, headers=headers)
        
        assert response.status_code == 200, "Getting feed"
        print(response.json())
        
        self.__class__.post_id = response.json()['posts'][0]['id']

        headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "feed")
        
        response = requests.get(endpoint, headers=headers)
        
        assert response.status_code == 200, "Getting feed"
        print(response.json())
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "feed")
        
        response = requests.get(
            endpoint, 
            headers=headers, 
            params={"filter":False})
        
        assert response.status_code == 200, "Getting feed"
        print(response.json())
        
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "feed/finished")
        
        response = requests.get(endpoint, headers=headers)
        
        assert response.status_code == 200, "Shouldn't be able to get finished reading"
        assert len(response.json()['posts']) == 0, "Shouldn't see any posts in finished reading"

    def test_get_awards(self):
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "awards")
        
        response = requests.get(endpoint, headers=headers)
        
        assert response.status_code == 200, "Getting awards"
        print(response.json())
        self.__class__.award_id = response.json()['awards'][0]['id']

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "awards")
        
        query_params = {"current_uses":True}

        response = requests.get(endpoint, headers=headers, params=query_params)
        
        assert response.status_code == 200, "Getting awards"
        print(response.json())

    def test_put_awards(self):
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            f"post/{self.post_id}/award/{self.award_id}")
        
        response = requests.put(endpoint, headers=headers)
        print(response.json())
        assert response.status_code == 200, "Putting Award"

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "feed")
        
        response = requests.get(endpoint, headers=headers)

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            f"post/{self.post_id}/award/{self.award_id}")
        
        response = requests.put(endpoint, headers=headers)
        print(response.json())
        assert response.status_code == 401, "Putting Award"
        
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            f"post/{self.post_id}/award/{self.award_id}")
        
        response = requests.delete(endpoint, headers=headers)
        print(response.json())
        assert response.status_code == 200, "deleting award"

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            f"post/{self.post_id}/award/{self.award_id}")
        
        response = requests.put(endpoint, headers=headers)
        print(response.json())
        assert response.status_code == 200, "Putting Award"

    def test_getting_awards_with_post(self):
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "awards")
        
        query_params = {
            "post_id": self.post_id
        }
        
        response = requests.get(endpoint, headers=headers, params=query_params)
        print(response.json())
        assert response.status_code == 200, "Getting awards"

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "awards")
        
        query_params = {
            "post_id": self.post_id,
            "current_uses": True
        }
        
        response = requests.get(endpoint, headers=headers, params=query_params)
        print(response.json())
        assert response.status_code == 200, "Getting awards"

    def test_minimal_preview(self):
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            f"minimal_preview/{self.user_id}/user")
        
        response = requests.get(endpoint, headers=headers)
        print(response.json())
        assert response.status_code == 200, "Getting minimal preview"

    def test_pressure_notifications(self):
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "create_notification")
        
        data = {
            "notification_type": "peer-pressure",
            "member_id": self.user_id_2
        }
        
        response = requests.post(endpoint, headers=headers, json=data)
        print(response.json())
        assert response.status_code == 200, "Posted pressure notification"

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "create_notification")
        
        data = {
            "notification_type": "peer-pressure",
            "member_id": self.user_id_2
        }
        
        response = requests.post(endpoint, headers=headers, json=data)
        print(response.json())
        assert response.status_code == 400, "Posted pressure notification too soon"

        headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/notifications_for_clubs/{self.user_id_2}")
    
        
        response = requests.get(endpoint, headers=headers)
        print(response.json())
        assert response.status_code == 200, "Got pressure notifications"
        notifications = response.json()['notifications']
        assert len(notifications) > 0, "No notifications found"

    def test_create_review(self):
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "review/create")
        
        data = {
            "user":{
                "id": self.user_id
            },
            "questions":[
                "Custom question"
            ],
            "ids":[
                -1
            ],
            "responses":[
                "test_response"
            ],
            "rating":0,
            "headline": "test_headline"
        }

        response = requests.post(
            endpoint,
            headers=headers,
            json=data
        )

        assert response.status_code == 200, "Creating Review"

        headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "review/create")
        
        data = {
            "user": {
                "id": self.user_id_2
            },
            "rating": 0
        }

        params = {"no_review":True}

        response = requests.post(
            endpoint,
            headers=headers,
            json=data,
            params=params
        )
        assert response.status_code == 200, "Finishing book"
        
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "feed/finished")
        
        response = requests.get(endpoint, headers=headers)
        
        assert response.status_code == 200, "Get finished reading feed"
        assert any([post['type'] == "club_review" for post in response.json()["posts"]])
        print(response.json())

    def test_deleting_member(self):
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        endpoint = (
            f"{self.endpoint}/api/bookclubs/{self.book_club_id}/"
            "remove_member")
        
        data = {
            "user_id": self.user_id_2
        }

        response = requests.delete(endpoint, headers=headers, json=data)
        assert response.status_code == 200, "Deleting Member"
        time.sleep(10)


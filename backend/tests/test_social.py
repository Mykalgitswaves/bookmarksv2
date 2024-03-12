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
    request.cls.password = "testpassword"
    request.cls.full_name = "Test User"
    
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

    request.cls.username_friend = "friend_user123"
    request.cls.email_friend = "frienduser@testemail.com"
    request.cls.password_friend = "testpassword"
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
class TestSocial:
    """
    Test class for social features such as friends, blocks and activities.
    """

    def test_friend_requests(self):
        """
        Test case for sending and accepting friend requests.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        response = requests.put(f"{self.endpoint}/api/user/{self.user_id_friend}/send_friend_request", headers=headers)
        assert response.status_code == 200, "Testing Send Friend Request"

        response = requests.put(f"{self.endpoint}/api/user/{self.user_id_friend}/unsend_friend_request", headers=headers)
        assert response.status_code == 200, "Testing Unsend Friend Request"

        response = requests.put(f"{self.endpoint}/api/user/{self.user_id_friend}/send_friend_request", headers=headers)
        assert response.status_code == 200, "Testing Send Friend Request"

        friend_headers = {"Authorization": f"{self.token_type_friend} {self.access_token_friend}"}
        response = requests.get(f"{self.endpoint}/api/user/{self.user_id_friend}/friend_requests", headers=friend_headers)
        assert response.status_code == 200, "Testing Get Friend Requests"
        friends_list = response.json()['data']
        print(friends_list)
        assert len(friends_list) == 1, "Testing Get Friend Requests"

        response = requests.put(f"{self.endpoint}/api/user/{self.user_id}/accept_friend_request", headers=friend_headers)
        assert response.status_code == 200, "Testing Accept Friend Request"

        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/friends", headers=headers)
        assert response.status_code == 200, "Testing Get Friends"
        friends_list = response.json()['data']
        print(friends_list)
        assert len(friends_list) == 1, "Testing Get Friends"

        response = requests.put(f"{self.endpoint}/api/user/{self.user_id}/remove_friend", headers=friend_headers)
        assert response.status_code == 200, "Testing remove friend"

        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/friends", headers=headers)
        assert response.status_code == 200, "Testing Get Friends"
        friends_list = response.json()['data']
        print(friends_list)
        assert len(friends_list) == 0, "Testing Get Friends"

    def test_decline_friend_request(self):
        """
        Test case for sending and accepting friend requests.
        """
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        response = requests.put(f"{self.endpoint}/api/user/{self.user_id_friend}/send_friend_request", headers=headers)
        assert response.status_code == 200, "Testing Send Friend Request"

        friend_headers = {"Authorization": f"{self.token_type_friend} {self.access_token_friend}"}
        response = requests.get(f"{self.endpoint}/api/user/{self.user_id_friend}/friend_requests", headers=friend_headers)
        assert response.status_code == 200, "Testing Get Friend Requests"
        friends_list = response.json()['data']
        print(friends_list)
        assert len(friends_list) == 1, "Testing Get Friend Requests"

        response = requests.put(f"{self.endpoint}/api/user/{self.user_id}/decline_friend_request", headers=friend_headers)
        assert response.status_code == 200, "Testing decline Friend Request"

        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/friends", headers=headers)
        assert response.status_code == 200, "Testing Get Friends"
        friends_list = response.json()['data']
        print(friends_list)
        assert len(friends_list) == 0, "Testing Get Friends"

    def test_block_user(self):
        """
        Test case for blocking and unblocking users.
        """ 
        # Set the headers with authorization token
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        response = requests.put(f"{self.endpoint}/api/user/{self.user_id_friend}/block", headers=headers)
        assert response.status_code == 200, "Testing Block User"

        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/blocked_users", headers=headers)
        assert response.status_code == 200, "Testing Get Blocked Users"
        blocked_users_list = response.json()['data']
        print(blocked_users_list)
        assert len(blocked_users_list) == 1, "Testing Get Blocked Users"

        response = requests.put(f"{self.endpoint}/api/user/{self.user_id_friend}/unblock", headers=headers)
        assert response.status_code == 200, "Testing Unblock User"

        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/blocked_users", headers=headers)
        assert response.status_code == 200, "Testing Get Blocked Users"
        blocked_users_list = response.json()['data']
        print(blocked_users_list)
        assert len(blocked_users_list) == 0, "Testing Get Blocked Users"

    def test_user_about(self):
        """
        Tests the user about endpoint
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/user_about", headers=headers)
        assert response.status_code == 200, "Testing User About"
        user_about = response.json()['data']
        print(user_about)

    def test_user_activities(self):
        """
        Tests the user activities endpoint
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        response = requests.get(f"{self.endpoint}/api/user/{self.user_id}/activity", headers=headers)
        assert response.status_code == 200, "Testing User Activities"
        user_activities = response.json()['data']
        print(user_activities)


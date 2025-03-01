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
    request.cls.username = "testuser123_posts"
    request.cls.email = "testuser_posts@testemail.com"
    request.cls.password = "testPassword1!"

    request.cls.username2 = "testuser123_posts2"
    request.cls.email2 = "testuser_posts2@testemail.com"
    request.cls.password2 = "testPassword1!"

    request.cls.book_id_in_db = "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872"
    request.cls.book_title_in_db = "Second Foundation"
    request.cls.book_small_img_url_in_db = "http://books.google.com/books/content?id=_uawAAAAIAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE732DLT-Q5P4M6ll9fpW5DH-Lz-FrGxwAQptgERj0vxnZYrLz57WvWzJ5k8Rr-OVQdQBOAImZNKuZQkgOgOO1HH2l5tUMj62Zngs0JbkXfsQIy3PcS_v8oHhB3XB7M0irmn4gM9g&source=gbs_api"
    
    request.cls.book_id_not_in_db = "gOCkJAAAAQAAJ"
    request.cls.book_title_not_in_db = "The Plain Speaker"
    request.cls.book_small_img_url_not_in_db = "http://books.google.com/books/content?id=OCkJAAAAQAAJ&printsec=frontcover&img=1&zoom=5&edge=curl&source=gbs_api"

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

    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Set Content-Type to application/json
    data = {
        "username": request.cls.username2,
        "email": request.cls.email2,
        "password": request.cls.password2,
    }
    response = requests.post(f"{request.cls.endpoint}/api/auth/signup", headers=headers, data=data)
    assert response.status_code == 200, "Creating Test User"

    request.cls.access_token_2 = response.json()["access_token"]
    request.cls.token_type_2 = response.json()["token_type"]
    request.cls.user_id_2 = response.json()["user_id"]

    yield

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username2, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"
    

@pytest.mark.usefixtures("setup_class")
class TestPosts:
    """
    Test class for post-related tests.
    """
    def test_create_review_book_in_db(self):
        """
        Test case to verify create review works

        Returns:
            None
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "book_id": self.book_id_in_db,
            "small_img_url": self.book_small_img_url_in_db,
            "title": self.book_title_in_db,
            "headline":"Test Headline",
            "questions":["Test Question 1","Test Question 2"],
            "ids":[-1,-1],
            "responses":["Response 1", "Response 2"],
            "spoilers":[False, True],
            "rating": 1
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_review", headers=headers, json=data)
        assert response.status_code == 200, "Testing create review"
        
        print(response.json())
        review_id = response.json()["data"]["id"]
        soft_delete_response = requests.delete(f"{self.endpoint}/api/posts/post/{review_id}/delete", headers=headers)
        assert soft_delete_response.status_code == 200, "Testing soft delete review"

        delete_data = {
            "post_id": review_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test review"

    def test_create_review_book_not_in_db(self):
        """
        Test case to verify create review works for a book not in the DB
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "book_id": self.book_id_not_in_db,
            "small_img_url": self.book_small_img_url_not_in_db,
            "title": self.book_title_not_in_db,
            "headline":"Test Headline",
            "questions":["Test Question 1","Test Question 2"],
            "ids":[-1,-1],
            "responses":["Response 1", "Response 2"],
            "spoilers":[False, True],
            "rating": 1
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_review", headers=headers, json=data)
        assert response.status_code == 200, "Testing create review not in DB"
        
        print(response.json())
        review_id = response.json()["data"]["id"]
        soft_delete_response = requests.delete(f"{self.endpoint}/api/posts/post/{review_id}/delete", headers=headers)
        assert soft_delete_response.status_code == 200, "Testing soft delete review"

        delete_data = {
            "post_id": review_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test review"

    def test_create_update_book_in_db(self):
        """
        Test case to verify create update works

        Returns:
            None
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "book_id": self.book_id_in_db,
            "small_img_url": self.book_small_img_url_in_db,
            "title": self.book_title_in_db,
            "headline":"Test Headline",
            "page": 1,
            "response":"Test Response",
            "is_spoiler":False,
            "quote":"Test Quote"
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_update", headers=headers, json=data)
        assert response.status_code == 200, "Testing create update"
        
        print(response.json())
        update_id = response.json()["data"]["id"]
        soft_delete_response = requests.delete(f"{self.endpoint}/api/posts/post/{update_id}/delete", headers=headers)
        assert soft_delete_response.status_code == 200, "Testing soft delete update"

        delete_data = {
            "post_id": update_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test update"

    def test_create_update_book_not_in_db(self):
        """
        Test case to verify create update works for a book not in the DB
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "book_id": self.book_id_in_db,
            "small_img_url": self.book_small_img_url_in_db,
            "title": self.book_title_in_db,
            "headline":"Test Headline",
            "page": 1,
            "response":"Test Response",
            "is_spoiler":False,
            "quote":"Test Quote"
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_update", headers=headers, json=data)
        assert response.status_code == 200, "Testing create update not in DB"
        
        print(response.json())
        update_id = response.json()["data"]["id"]
        soft_delete_response = requests.delete(f"{self.endpoint}/api/posts/post/{update_id}/delete", headers=headers)
        assert soft_delete_response.status_code == 200, "Testing soft delete update"

        delete_data = {
            "post_id": update_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test update"

    def test_create_comparison_book_in_db(self):
        """
        Test case to verify create comparison works

        Returns:
            None
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "book_ids": [self.book_id_in_db, self.book_id_not_in_db],
            "book_small_imgs": [self.book_small_img_url_in_db, self.book_small_img_url_not_in_db],
            "book_titles": [self.book_title_in_db, self.book_title_not_in_db],
            "comparator_topics":["comparator1","comparator2"],
            "comparator_ids":[-1,-1],
            "responses":["test1","test2"],
            "book_specific_headlines":["book1headline","book2headline"]
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_comparison", headers=headers, json=data)
        assert response.status_code == 200, "Testing create comparison"
        
        print(response.json())
        comparison_id = response.json()["data"]["id"]
        soft_delete_response = requests.delete(f"{self.endpoint}/api/posts/post/{comparison_id}/delete", headers=headers)
        assert soft_delete_response.status_code == 200, "Testing soft delete comparison"

        delete_data = {
            "post_id": comparison_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test comparison"

    def test_create_recommendation_friend_book_in_db(self):
        """
        Test case to verify create recommendation_friend works

        Returns:
            None
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "book_id": self.book_id_in_db,
            "small_img_url": self.book_small_img_url_in_db,
            "title": self.book_title_in_db,
            "to_user_username":self.username2,
            "to_user_text": "test1",
            "from_user_text":"test2"
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_recommendation_friend", headers=headers, json=data)
        assert response.status_code == 200, "Testing create recommendation_friend"
        
        print(response.json())
        recommendation_friend_id = response.json()["data"]["id"]
        soft_delete_response = requests.delete(f"{self.endpoint}/api/posts/post/{recommendation_friend_id}/delete", headers=headers)
        assert soft_delete_response.status_code == 200, "Testing soft delete recommendation_friend"

        delete_data = {
            "post_id": recommendation_friend_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test recommendation_friend"

    def test_create_recommendation_friend_book_not_in_db(self):
        """
        Test case to verify create recommendation_friend works for a book not in the DB
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "book_id": self.book_id_in_db,
            "small_img_url": self.book_small_img_url_in_db,
            "title": self.book_title_in_db,
            "to_user_username":self.username2,
            "to_user_text": "test1",
            "from_user_text":"test2"
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_recommendation_friend", headers=headers, json=data)
        assert response.status_code == 200, "Testing create recommendation_friend not in DB"
        
        print(response.json())
        recommendation_friend_id = response.json()["data"]["id"]
        soft_delete_response = requests.delete(f"{self.endpoint}/api/posts/post/{recommendation_friend_id}/delete", headers=headers)
        assert soft_delete_response.status_code == 200, "Testing soft delete recommendation_friend"

        delete_data = {
            "post_id": recommendation_friend_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test recommendation_friend"

    def test_milestone(self):
        """
        Test case to verify create milestone works for a book not in the DB
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "num_books": 10
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_milestone", headers=headers, json=data)
        assert response.status_code == 200, "Testing create milestone not in DB"
        
        print(response.json())
        milestone_id = response.json()["data"]["id"]
        soft_delete_response = requests.delete(f"{self.endpoint}/api/posts/post/{milestone_id}/delete", headers=headers)
        assert soft_delete_response.status_code == 200, "Testing soft delete milestone"

        delete_data = {
            "post_id": milestone_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test milestone"

    def test_get_posts(self):
        """
        Test case to verify get posts works
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "num_books": 10
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_milestone", headers=headers, json=data)
        assert response.status_code == 200, "Testing create milestone not in DB"
        
        milestone_id = response.json()["data"]["id"]

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        response = requests.get(f"{self.endpoint}/api/posts/me", headers=headers)
        assert response.status_code == 200, "Testing get posts"
        print(response.json()['data'][0])
        assert len(response.json()['data']) > 0, "Testing get posts"

        response = requests.get(f"{self.endpoint}/api/posts/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Testing get posts by id"
        print(response.json()['data'][0])
        assert len(response.json()['data']) > 0, "Testing get posts  by id"

        response = requests.get(f"{self.endpoint}/api/posts/post/{milestone_id}", headers=headers)
        assert response.status_code == 200, "Testing get post by id"

        delete_data = {
            "post_id": milestone_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test milestone"

    def test_comments(self):
        """
        Test case to verify create and get comments and replies works
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "num_books": 10
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_milestone", headers=headers, json=data)
        assert response.status_code == 200, "Testing create milestone not in DB"
        
        milestone_id = response.json()["data"]["id"]

        data = {
            "post_id": milestone_id,
            "text":"Test Comment",
            "replied_to":None
        }

        response = requests.post(f"{self.endpoint}/api/posts/comment/create", headers=headers, json=data)

        print(response.json())
        assert response.status_code == 200, "Testing create comment"
        
        comment_id = response.json()["data"]["id"]

        response = requests.get(f"{self.endpoint}/api/posts/post/{milestone_id}/comments", headers=headers)

        print(response.json())
        assert response.status_code == 200, "Testing get comments"
        assert len(response.json()['data']['comments']) > 0, "Testing get comments"

        response = requests.get(
            f"{self.endpoint}/api/posts/post/{milestone_id}/comments", 
            headers=headers
            )

        # print(response.json())
        # assert response.status_code == 200, "Testing get comments new"
        # assert len(response.json()['data']['comments']) > 0, "Testing get comments"

        data = {
            "post_id": milestone_id,
            "text":"Test Comment Level 1",
            "replied_to":comment_id
        }

        response = requests.post(f"{self.endpoint}/api/posts/comment/create", headers=headers, json=data)

        print(response.json())
        assert response.status_code == 200, "Testing create comment with reply"

        comment_1_id = response.json()["data"]["id"]

        data = {
            "post_id": milestone_id,
            "text":"Test Comment Level 2",
            "replied_to":comment_1_id
        }

        response = requests.post(f"{self.endpoint}/api/posts/comment/create", headers=headers, json=data)

        print(response.json())
        assert response.status_code == 200, "Testing create comment with reply"

        comment_2_id = response.json()["data"]["id"]

        response = requests.get(
            f"{self.endpoint}/api/posts/post/{milestone_id}/comments", 
            headers=headers
            )

        print(response.json())
        # assert response.status_code == 200, "Testing get comments new"
        # assert len(response.json()['data']['comments']) > 0, "Testing get comments"

        headers_2 = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}

        data = {
            "post_id": milestone_id,
            "text":"Test Comment Level 0",
            "replied_to":None
        }

        response = requests.post(f"{self.endpoint}/api/posts/comment/create", headers=headers_2, json=data)

        print(response.json())
        assert response.status_code == 200, "Testing create comment"

        comment_0_id = response.json()["data"]["id"]

        data = {
            "post_id": milestone_id,
            "text":"Test Comment Level 1",
            "replied_to":comment_0_id
        }

        response = requests.post(f"{self.endpoint}/api/posts/comment/create", headers=headers, json=data)

        print(response.json())
        assert response.status_code == 200, "Testing create comment with reply"

        comment_1_id = response.json()["data"]["id"]

        data = {
            "post_id": milestone_id,
            "text":"Test Comment Level 2",
            "replied_to":comment_1_id
        }

        response = requests.post(f"{self.endpoint}/api/posts/comment/create", headers=headers_2, json=data)

        print(response.json())
        assert response.status_code == 200, "Testing create comment with reply"

        response = requests.get(
            f"{self.endpoint}/api/posts/post/{milestone_id}/comments", 
            headers=headers
            )

        print(response.json())
        assert response.status_code == 200, "Testing get comments new"
        assert len(response.json()['data']['comments']) > 0, "Testing get comments"

        response = requests.get(f"{self.endpoint}/api/posts/comment/{comment_id}/replies", headers=headers)
        assert response.status_code == 200, "Testing get replies"
        assert len(response.json()['data']) > 0, "Testing get replies"


        response = requests.put(f"{self.endpoint}/api/posts/comment/{comment_id}/delete", headers=headers)
        assert response.status_code == 200, "Testing delete comment"\

        delete_data = {
            "post_id": milestone_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test milestone"

    def test_likes(self):
        """
        Test case to verify like and unlike works for posts and comments
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "num_books": 10
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_milestone", headers=headers, json=data)
        assert response.status_code == 200, "Testing create milestone not in DB"
        
        milestone_id = response.json()["data"]["id"]

        data = {
            "post_id": milestone_id,
            "text":"Test Comment",
            "replied_to":None
        }

        response = requests.post(f"{self.endpoint}/api/posts/comment/create", headers=headers, json=data)

        print(response.json())
        assert response.status_code == 200, "Testing create comment"
        
        comment_id = response.json()["data"]["id"]

        response = requests.put(f"{self.endpoint}/api/posts/post/{milestone_id}/like", headers=headers)
        assert response.status_code == 200, "Testing like post"

        response = requests.put(f"{self.endpoint}/api/posts/post/{milestone_id}/remove_like", headers=headers)
        assert response.status_code == 200, "Testing remove_like post"

        response = requests.put(f"{self.endpoint}/api/posts/comment/{comment_id}/like", headers=headers)
        assert response.status_code == 200, "Testing like comment"

        response = requests.put(f"{self.endpoint}/api/posts/comment/{comment_id}/remove_like", headers=headers)
        assert response.status_code == 200, "Testing remove_like comment"

        delete_data = {
            "post_id": milestone_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test milestone"

    def test_pin_comment(self):
        """
        Test case to verify pin and unpin works for comments
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "num_books": 10
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_milestone", headers=headers, json=data)
        assert response.status_code == 200, "Testing create milestone not in DB"
        
        milestone_id = response.json()["data"]["id"]

        data = {
            "post_id": milestone_id,
            "text":"Test Comment",
            "replied_to":None
        }

        response = requests.post(f"{self.endpoint}/api/posts/comment/create", headers=headers, json=data)

        print(response.json())
        assert response.status_code == 200, "Testing create comment"

        comment_id = response.json()["data"]["id"]

        response = requests.put(f"{self.endpoint}/api/posts/post/{milestone_id}/pin/{comment_id}", headers=headers)
        assert response.status_code == 200, "Testing pin comment"

        response = requests.get(f"{self.endpoint}/api/posts/post/{milestone_id}/pinned_comments", headers=headers)
        assert response.status_code == 200, "Testing getting a pinned comment"
        assert len(response.json()['data']) > 0, "Testing getting a pinned comment"

        response = requests.get(f"{self.endpoint}/api/posts/post/{milestone_id}/comments", headers=headers)
        assert response.status_code == 200, "Testing getting a pinned comment"
        assert len(response.json()['data']['pinned_comments']) > 0, "Testing getting a pinned comment"

        response = requests.put(f"{self.endpoint}/api/posts/post/{milestone_id}/remove_pin/{comment_id}", headers=headers)
        assert response.status_code == 200, "Testing remove pin"

        response = requests.get(f"{self.endpoint}/api/posts/post/{milestone_id}/pinned_comments", headers=headers)
        assert response.status_code == 200, "Testing pinned comment removed"
        assert len(response.json()['data']) == 0, "Testing pinned comment removed"

        delete_data = {
            "post_id": milestone_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test milestone"

    def test_feed(self):
        """
        tests the general feed endpoint
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        response = requests.get(f"{self.endpoint}/api/posts", headers=headers)
        assert response.status_code == 200, "Testing feed"
        assert len(response.json()['data']) > 0, "Testing feed"

    def test_too_long_post(self):
        """
        Tests if the correct error is thrown when the response field is too long
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}

        data = {
            "book_id": self.book_id_in_db,
            "small_img_url": self.book_small_img_url_in_db,
            "title": self.book_title_in_db,
            "headline":"Test Headline",
            "questions":["Test Question 1","Test Question 2"],
            "ids":[-1,-1],
            "responses":["a"*10001, "Response 2"],
            "spoilers":[False, True],
            "rating": 1
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_review", headers=headers, json=data)
        print(response.json()['detail'])
        assert response.status_code == 400, "Testing too long response"

        data = {
            "book_id": self.book_id_in_db,
            "small_img_url": self.book_small_img_url_in_db,
            "title": self.book_title_in_db,
            "headline":"a"*1000,
            "questions":["Test Question 1","Test Question 2"],
            "ids":[-1,-1],
            "responses":["a", "Response 2"],
            "spoilers":[False, True],
            "rating": 1
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_review", headers=headers, json=data)
        print(response.json()['detail'])
        assert response.status_code == 400, "Testing too long headline"

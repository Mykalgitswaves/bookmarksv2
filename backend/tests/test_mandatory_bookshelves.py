import pytest
from httpx import AsyncClient
import requests
import json
import time
import asyncio
import websockets

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
    request.cls.username = "testuser123_shelves"
    request.cls.email = "testuser_shelves@testemail.com"
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

    request.cls.username_2 = "testuser123_shelves_2"
    request.cls.email_2 = "testuser_shelves_2@testemail.com"
    request.cls.password_2 = "testpassworD1!"

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

    yield

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username_2, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

@pytest.mark.usefixtures("setup_class")
class TestBookshelfMandatory:
    """
    Test class for Mandatory bookshelves
    """
    def test_get_bookshelves(self):
        """
        Test case to check the get endpoints for the mandatory shelves
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}  # Set Authorization header
        response = requests.get(f"{self.endpoint}/api/bookshelves/want_to_read/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Want to Read Shelf"
        print(response.json())
        bookshelf_id = response.json()["bookshelf"]["id"]

        # Test with the bookshelf_id endpoint
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Get Want to Read Shelf by ID"

        response = requests.get(f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Currently Reading Shelf"
        bookshelf_id = response.json()["bookshelf"]["id"]

        # Test with the bookshelf_id endpoint
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Get Currently Reading Shelf by ID"

        response = requests.get(f"{self.endpoint}/api/bookshelves/finished_reading/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Finished Reading Shelf"
        bookshelf_id = response.json()["bookshelf"]["id"]

        # Test with the bookshelf_id endpoint
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Get Finished Reading Shelf by ID"

    def test_bookshelf_previews(self):
        """
        Test case to check the get preview endpoints for the mandatory shelves
        """

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        response = requests.get(f"{self.endpoint}/api/bookshelves/want_to_read/{self.user_id}/preview", headers=headers)
        assert response.status_code == 200, "Get Want to Read Shelf Preview"
        print(response.json())

        response = requests.get(f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}/preview", headers=headers)
        assert response.status_code == 200, "Get Currently Reading Shelf Preview"
        print(response.json())

        response = requests.get(f"{self.endpoint}/api/bookshelves/finished_reading/{self.user_id}/preview", headers=headers)
        assert response.status_code == 200, "Get Finished Reading Shelf Preview"
        print(response.json())

    def test_quick_add(self):
        """
        Test case to check the quick add endpoints for the mandatory shelves
        """
        book_data_1 = {
            	"book" : {
                    "id" : "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872",
                    "author_names": ["Isaac Asimov"],
                    "title": "Foundation",
                    "small_img_url": "http://books.google.com/books/content?id=_uawAAAAIAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE732DLT-Q5P4M6ll9fpW5DH-Lz-FrGxwAQptgERj0vxnZYrLz57WvWzJ5k8Rr-OVQdQBOAImZNKuZQkgOgOO1HH2l5tUMj62Zngs0JbkXfsQIy3PcS_v8oHhB3XB7M0irmn4gM9g&source=gbs_api"
                }
        }

        book_data_2 = {
            	"book" : {
                    "id" : "caaaedd16-11c7-4d74-8eb2-985537223d40",
                    "author_names": ["Maggie O'Farrell"],
                    "title": "The Marriage Portrait",
                    "small_img_url": "http://books.google.com/books/content?id=AnuczwEACAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE731cxkg3iRmy3ma5pIYhwtWMGlHSNK8oLk9FpLma-TJyfRdn-HbMz8tHjn3TPlvkBh-wPX7n2A6aVp-7_iymmoqcq7R62gaAt5Fp2cTuYIj34066LqjZMTdQiEnTodmHTSNLj9I&source=gbs_api"
                }
        }

        book_data_3 = {
            	"book" : {
                    "id" : "c57fbe3df-9a61-41e7-a3e9-576f17a29c50",
                    "author_names": ["Maya Phillips"],
                    "title": "Nerd",
                    "small_img_url": "http://books.google.com/books/publisher/content?id=483DEAAAQBAJ&printsec=frontcover&img=1&zoom=5&edge=curl&imgtk=AFLRE70x2bq6tvfuT2n_5ziJqrSWL2Lb1Iu5LiqLZTc0rH5AJTThqQ7K6N26LKGRoQe4LwJyjky9lPNdJs6nckmcOKhslPTVsyaT_jyJAAb9qHeZEM_wXHCLMLmVwyNBV_MuC4dxojW1&source=gbs_api"
                }
        }

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        response = requests.put(f"{self.endpoint}/api/bookshelves/quick_add/want_to_read/", 
                                 json=book_data_1, headers=headers)
        assert response.status_code == 200, "Quick Add to Want to Read Shelf"
        print(response.json(), "quick add want to read")

        response = requests.get(f"{self.endpoint}/api/bookshelves/want_to_read/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Want to Read Shelf"
        print(response.json(), "get want to read")
        assert book_data_1["book"]["id"] in [book['id'] for book in response.json()["bookshelf"]["books"]], "Book not added to Want to Read Shelf"

        response = requests.put(f"{self.endpoint}/api/bookshelves/quick_add/currently_reading/", 
                                 json=book_data_2, headers=headers)
        assert response.status_code == 200, "Quick Add to Currently Reading Shelf"
        print(response.json(), "quick add currently reading")

        response = requests.get(f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Currently Reading Shelf"
        print(response.json(), "get currently reading")
        assert book_data_2["book"]["id"] in [book['id'] for book in response.json()["bookshelf"]["books"]], "Book not added to Currently Reading Shelf"

        response = requests.put(f"{self.endpoint}/api/bookshelves/quick_add/finished_reading/", 
                                 json=book_data_3, headers=headers)
        assert response.status_code == 200, "Quick Add to Finished Reading Shelf"
        print(response.json(), "quick add finished reading")

        response = requests.get(f"{self.endpoint}/api/bookshelves/finished_reading/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Finished Reading Shelf"
        print(response.json(), "get finished reading")
        assert book_data_3["book"]["id"] in [book['id'] for book in response.json()["bookshelf"]["books"]], "Book not added to Finished Reading Shelf"

        response = requests.put(f"{self.endpoint}/api/bookshelves/quick_add/currently_reading?move_from=want_to_read", 
                                 json=book_data_1, headers=headers)
        assert response.status_code == 200, "Quick Add to Currently Reading Shelf"
        print(response.json(), "quick add currently reading from want to read")

        response = requests.get(f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Currently Reading Shelf"
        print(response.json(), "get currently reading")
        assert book_data_1["book"]["id"] in [book['id'] for book in response.json()["bookshelf"]["books"]], "Book not added to Currently Reading Shelf"

        response = requests.get(f"{self.endpoint}/api/bookshelves/want_to_read/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Want to Read Shelf"
        print(response.json(), "get want to read")
        assert book_data_1["book"]["id"] not in [book['id'] for book in response.json()["bookshelf"]["books"]], "Book not removed from Want to Read Shelf"

    def test_post_creation_trigger(self):
        """
        This checks if a WantToReadPost object is created when a book is added to the Want to Read shelf
        """
        book_data_1 = {
            	"book" : {
                    "id" : "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872",
                    "author_names": ["Isaac Asimov"],
                    "title": "Foundation",
                    "small_img_url": "http://books.google.com/books/content?id=_uawAAAAIAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE732DLT-Q5P4M6ll9fpW5DH-Lz-FrGxwAQptgERj0vxnZYrLz57WvWzJ5k8Rr-OVQdQBOAImZNKuZQkgOgOO1HH2l5tUMj62Zngs0JbkXfsQIy3PcS_v8oHhB3XB7M0irmn4gM9g&source=gbs_api"
                }
        }

        book_data_2 = {
            	"book" : {
                    "id" : "caaaedd16-11c7-4d74-8eb2-985537223d40",
                    "author_names": ["Maggie O'Farrell"],
                    "title": "The Marriage Portrait",
                    "small_img_url": "http://books.google.com/books/content?id=AnuczwEACAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE731cxkg3iRmy3ma5pIYhwtWMGlHSNK8oLk9FpLma-TJyfRdn-HbMz8tHjn3TPlvkBh-wPX7n2A6aVp-7_iymmoqcq7R62gaAt5Fp2cTuYIj34066LqjZMTdQiEnTodmHTSNLj9I&source=gbs_api"
                }
        }

        book_data_3 = {
            	"book" : {
                    "id" : "c57fbe3df-9a61-41e7-a3e9-576f17a29c50",
                    "author_names": ["Maya Phillips"],
                    "title": "Nerd",
                    "small_img_url": "http://books.google.com/books/publisher/content?id=483DEAAAQBAJ&printsec=frontcover&img=1&zoom=5&edge=curl&imgtk=AFLRE70x2bq6tvfuT2n_5ziJqrSWL2Lb1Iu5LiqLZTc0rH5AJTThqQ7K6N26LKGRoQe4LwJyjky9lPNdJs6nckmcOKhslPTVsyaT_jyJAAb9qHeZEM_wXHCLMLmVwyNBV_MuC4dxojW1&source=gbs_api"
                }
        }

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        response = requests.put(f"{self.endpoint}/api/bookshelves/quick_add/want_to_read/", 
                                 json=book_data_1, headers=headers)
        assert response.status_code == 200, "Quick Add to Want to Read Shelf"
        print(response.json(), "quick add want to read")

        time.sleep(2)

        response = requests.get(f"{self.endpoint}/api/posts/me", headers=headers)
        assert response.status_code == 200, "Get Posts"
        assert response.json()['data'][0]['type'] == 'want_to_read_post', "Want to Read Post not created"

        response = requests.put(f"{self.endpoint}/api/bookshelves/quick_add/currently_reading/", 
                                 json=book_data_3, headers=headers)
        
        assert response.status_code == 200, "Quick Add to Currently Reading Shelf"
        print(response.json(), "quick add currently reading")

        time.sleep(2)

        response = requests.get(f"{self.endpoint}/api/posts/{self.user_id}", headers=headers)
        assert response.status_code == 200, "Get Posts"
        assert response.json()['data'][0]['type'] == 'currently_reading_post', "Currently Reading Post not created"

        response = requests.get(f"{self.endpoint}/api/posts/post/{response.json()['data'][0]['id']}", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Get Post"
        
    def test_currently_reading_preview(self):
        book_data_1 = {
            "book" : {
                "id" : "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872",
                "author_names": ["Isaac Asimov"],
                "title": "Foundation",
                "small_img_url": "http://books.google.com/books/content?id=_uawAAAAIAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE732DLT-Q5P4M6ll9fpW5DH-Lz-FrGxwAQptgERj0vxnZYrLz57WvWzJ5k8Rr-OVQdQBOAImZNKuZQkgOgOO1HH2l5tUMj62Zngs0JbkXfsQIy3PcS_v8oHhB3XB7M0irmn4gM9g&source=gbs_api"
            }
        }
        
        book_data_2 = {
            	"book" : {
                    "id" : "caaaedd16-11c7-4d74-8eb2-985537223d40",
                    "author_names": ["Maggie O'Farrell"],
                    "title": "The Marriage Portrait",
                    "small_img_url": "http://books.google.com/books/content?id=AnuczwEACAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE731cxkg3iRmy3ma5pIYhwtWMGlHSNK8oLk9FpLma-TJyfRdn-HbMz8tHjn3TPlvkBh-wPX7n2A6aVp-7_iymmoqcq7R62gaAt5Fp2cTuYIj34066LqjZMTdQiEnTodmHTSNLj9I&source=gbs_api"
                }
        }

        book_data_3 = {
            	"book" : {
                    "id" : "c57fbe3df-9a61-41e7-a3e9-576f17a29c50",
                    "author_names": ["Maya Phillips"],
                    "title": "Nerd",
                    "small_img_url": "http://books.google.com/books/publisher/content?id=483DEAAAQBAJ&printsec=frontcover&img=1&zoom=5&edge=curl&imgtk=AFLRE70x2bq6tvfuT2n_5ziJqrSWL2Lb1Iu5LiqLZTc0rH5AJTThqQ7K6N26LKGRoQe4LwJyjky9lPNdJs6nckmcOKhslPTVsyaT_jyJAAb9qHeZEM_wXHCLMLmVwyNBV_MuC4dxojW1&source=gbs_api"
                }
        }

        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        
        response = requests.get(f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}/front_page", 
                                headers=headers)
        assert response.status_code == 200, "Currently Reading front_page"
        print(response.json(), "currently reading front_page first, \n") 
        
        data = {
            "book_id": "c57fbe3df-9a61-41e7-a3e9-576f17a29c50",
            "small_img_url": "http://books.google.com/books/publisher/content?id=483DEAAAQBAJ&printsec=frontcover&img=1&zoom=5&edge=curl&imgtk=AFLRE70x2bq6tvfuT2n_5ziJqrSWL2Lb1Iu5LiqLZTc0rH5AJTThqQ7K6N26LKGRoQe4LwJyjky9lPNdJs6nckmcOKhslPTVsyaT_jyJAAb9qHeZEM_wXHCLMLmVwyNBV_MuC4dxojW1&source=gbs_api",
            "title": "Nerd",
            "headline":"Test Headline",
            "page": 1,
            "response":"Test Response",
            "is_spoiler":False,
            "quote":"Test Quote"
        }
        
        response = requests.post(f"{self.endpoint}/api/posts/create_update", headers=headers, json=data)
        assert response.status_code == 200, "Testing create update \n"
        print(response.json())
        update_id = response.json()["data"]["id"]
        
        response = requests.get(f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}/front_page", 
                                headers=headers)
        assert response.status_code == 200, "Currently Reading front_page"
        print(response.json(), "currently reading front_page first \n")
        first_book = response.json()['bookshelf']['books'][0]
        assert first_book['id'] == "c57fbe3df-9a61-41e7-a3e9-576f17a29c50"
        assert first_book['current_page'] == 1

        data = {
            "starting_page_for_range": 0,
            "size_of_range": 20,
        }

        response = requests.get(
            f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}/currently_reading_book/c57fbe3df-9a61-41e7-a3e9-576f17a29c50/updates_for_current_page",
            headers=headers,
            params=data)
        assert response.status_code == 200, "Currently Reading updates for current page"
        print(response.json(), "currently reading updates for current page \n")
        assert response.json()['additional_updates_not_shown'] == 0, "Currently Reading updates for current page counts"
        assert len(response.json()['updates']) == 1, "Currently Reading updates for current page data"

        response = requests.get(
            f"{self.endpoint}/api/bookshelves/progress_bar/{self.user_id}/book/c57fbe3df-9a61-41e7-a3e9-576f17a29c50/updates",
            headers=headers)
        assert response.status_code == 200, "Currently Reading progress bar"
        print(response.json(), "currently reading progress bar response \n")
        
        data = {
            "book_id" : "c57fbe3df-9a61-41e7-a3e9-576f17a29c50",
            "new_current_page": 5
        }
        
        response = requests.put(f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}/update_current_page", 
                                headers=headers,
                                json=data)
        assert response.status_code == 200, "Update page quick"
        print(response.json(), "update page quick \n")
        
        response = requests.get(f"{self.endpoint}/api/bookshelves/currently_reading/{self.user_id}/front_page", 
                                headers=headers)
        assert response.status_code == 200, "Currently Reading front_page"
        print(response.json(), "currently reading front_page first \n")
        first_book = response.json()['bookshelf']['books'][0]
        assert first_book['id'] == "c57fbe3df-9a61-41e7-a3e9-576f17a29c50"
        assert first_book['current_page'] == 5
        
        
        
        soft_delete_response = requests.delete(f"{self.endpoint}/api/posts/post/{update_id}/delete", headers=headers)
        assert soft_delete_response.status_code == 200, "Testing soft delete update"

        delete_data = {
            "post_id": update_id,
            "admin_credentials": self.admin_credentials
        }

        hard_delete_response = requests.post(f"{self.endpoint}/api/admin/delete_post_and_comments", json=delete_data)
        assert hard_delete_response.status_code == 200, "Hard delete of test update"
        
        




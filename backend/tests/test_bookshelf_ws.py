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
    request.cls.password = "testpassword"

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
    request.cls.password_2 = "testpassword"

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
class TestBookshelfWS:
    """
    Test class for Websocket operations on Bookshelves
    """
    def test_create_bookshelf(self):
        """
        Test case to create a bookshelf.

        This test case sends a POST request to create a bookshelf with the specified name, description, and visibility.
        It then sends a GET request to retrieve the created bookshelf and verifies that the response status code is 200.
        Finally, it sends a DELETE request to delete the created bookshelf and verifies that the response status code is 200.

        Returns:
            None
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }

        # Send a POST request to create a bookshelf
        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"
        bookshelf_id = response.json()["bookshelf_id"]

        # Send a GET request to retrieve the created bookshelf
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"

        # Send a DELETE request to delete the created bookshelf
        response = requests.delete(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/delete", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Deleting Bookshelf"

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """
        Test case to check the websocket connection to the bookshelf.
        """
        # Prepare headers and data for the requests
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }

        # Create a bookshelf
        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"
        bookshelf_id = response.json()["bookshelf_id"]

        # Get the created bookshelf
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"

        # Connect to the websocket
        uri = f"ws://127.0.0.1:8000/api/bookshelves/ws/{bookshelf_id}?token={self.access_token}"
        async with websockets.connect(uri) as ws:
            assert ws.open, "Websocket Connection"

            # Receive the websocket token
            response = await ws.recv()
            ws_token = json.loads(response)['token']
            assert ws_token, "Websocket Token Not Received"

            # Send data to the server
            small_img_url = "http://books.google.com/books/content?id=_uawAAAAIAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE732DLT-Q5P4M6ll9fpW5DH-Lz-FrGxwAQptgERj0vxnZYrLz57WvWzJ5k8Rr-OVQdQBOAImZNKuZQkgOgOO1HH2l5tUMj62Zngs0JbkXfsQIy3PcS_v8oHhB3XB7M0irmn4gM9g&source=gbs_api"
            data_to_send = {"type": "add", "token": ws_token, "book": {"title": "Second Foundation", 
                                                                       "small_img_url": small_img_url,
                                                                       "author_names": ["Isaac Asimov"],
                                                                       "id": "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872",
                                                                       "note_for_shelf": "This is a note for the shelf."}}
            await ws.send(json.dumps(data_to_send))

            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response:", response_after_completion)

            # Send duplicate data to the server
            await ws.send(json.dumps(data_to_send))

            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response on duplicate:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response on duplicate:", response_after_completion)

            # Send data to remove a book from the server
            data_to_send = {"type": "delete", "token": ws_token, "target_id": "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872"}
            await ws.send(json.dumps(data_to_send))

            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response on remove:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response on remove:", response_after_completion)

            # Send data to add a book to the server
            data_to_send = {"type": "add", "token": ws_token, "book": {"title": "Second Foundation", 
                                                                       "small_img_url": small_img_url,
                                                                       "author_names": ["Isaac Asimov"],
                                                                       "id": "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872"}}
            await ws.send(json.dumps(data_to_send))

            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response:", response_after_completion)

            # Send a request to the update bookself note endpoint
            request_data = {"note_for_shelf": "This is a new note for the shelf.",
                            "book_id": "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872"}
            response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/update_book_note", headers=headers, json=request_data)
            assert response.status_code == 200, "Updating Note"

            # Get the websocket response after updating the note
            response_after_sending = await ws.recv()
            print("Server response:", response_after_sending)

            # Send a request to the update bookself note endpoint
            request_data = {"note_for_shelf": None,
                            "book_id": "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872"}
            response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/update_book_note", headers=headers, json=request_data)
            assert response.status_code == 200, "Updating Note"

            # Get the websocket response after updating the note
            response_after_sending = await ws.recv()
            print("Server response:", response_after_sending)

            # Send data to add another book to the server
            small_img_url = "http://books.google.com/books/publisher/content?id=zJiJDQAAQBAJ&printsec=frontcover&img=1&zoom=5&edge=curl&imgtk=AFLRE7101pEA1qPqLGWj3HZGYk066aVnUx5od6ELqnAUw6y7YJyuaCg67i-feAewSsl9o0_ya__x6cl7HlnlEPLkxS1MtkyDzlgXO3s0KVRzcahD0_9gOYwFQPfJkqrQtUOdeffhxQSL&source=gbs_api"
            data_to_send = {"type": "add", "token": ws_token, "book": {"title": "What Are You Looking At?", 
                                                                       "small_img_url": small_img_url,
                                                                       "author_names": ["Will Gompertz"],
                                                                       "id": "c5af309c7-3ac9-4d32-a7ce-32cbe818c15d"}}
            await ws.send(json.dumps(data_to_send))

            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response:", response_after_completion)

            # Send data to reorder books on the server
            data_to_send = {"type": "reorder", 
                            "token": ws_token, 
                            "target_id": "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872", 
                            "previous_book_id": "c5af309c7-3ac9-4d32-a7ce-32cbe818c15d",
                            "next_book_id": None}
            await ws.send(json.dumps(data_to_send))

            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response:", response_after_completion)

        # Delete the created bookshelf
        response = requests.delete(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/delete", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Deleting Bookshelf"

    def test_change_title(self):
        """
        Test case to create a bookshelf.
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }

        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"
        bookshelf_id = response.json()["bookshelf_id"]

        data = {
            "title": "New Title"
        }

        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/update_title", headers=headers, json=data)
        assert response.status_code == 200, "Updating Bookshelf"

        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"
        assert response.json()['bookshelf']["title"] == "New Title", "Title Updated"

        response = requests.delete(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/delete", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Deleting Bookshelf"

    def test_change_description(self):
        """
        Test case to change the description of a bookshelf.

        This test case performs the following steps:
        1. Creates a new bookshelf with a name, description, and visibility.
        2. Updates the description of the bookshelf.
        3. Retrieves the bookshelf and verifies that the description has been updated.
        4. Deletes the bookshelf.

        Note: This test assumes that the user is already authenticated and has a valid access token.

        """

        # Step 1: Create a new bookshelf
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }

        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"

        bookshelf_id = response.json()["bookshelf_id"]

        # Step 2: Update the description of the bookshelf
        data = {
            "description": "New Description"
        }

        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/update_description", headers=headers, json=data)
        assert response.status_code == 200, "Updating Bookshelf"

        # Step 3: Retrieve the bookshelf and verify the description has been updated
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"
        assert response.json()['bookshelf']["description"] == "New Description", "Description Updated"

        # Step 4: Delete the bookshelf
        response = requests.delete(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/delete", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Deleting Bookshelf"

    def test_change_visibility(self):
        """
        Test case to change the visibility of a bookshelf.

        This test case performs the following steps:
        1. Creates a bookshelf with public visibility.
        2. Updates the visibility of the bookshelf to private.
        3. Retrieves the bookshelf and verifies that the visibility has been updated.
        4. Deletes the bookshelf.

        Note: This test assumes that the user is already authenticated and has a valid access token.

        """

        # Step 1: Create a bookshelf with public visibility
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }
        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"
        bookshelf_id = response.json()["bookshelf_id"]

        # Step 2: Update the visibility of the bookshelf to private
        data = {
            "visibility": "private"
        }
        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/update_visibility", headers=headers, json=data)
        assert response.status_code == 200, "Updating Bookshelf"

        # Step 3: Retrieve the bookshelf and verify that the visibility has been updated
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"
        assert response.json()['bookshelf']["visibility"] == "private", "Visibility Updated"

        # Step 4: Delete the bookshelf
        response = requests.delete(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/delete", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Deleting Bookshelf"

    def test_contributors(self):
        """
        Test case to test adding and removing contributors
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }

        # Create a bookshelf
        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"

        bookshelf_id = response.json()["bookshelf_id"]

        data = {
            "contributor_id": self.user_id_2
        }

        # Add a contributor to the bookshelf
        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/add_contributor", headers=headers, json=data)
        assert response.status_code == 200, "Adding Contributor"

        # Get the bookshelf
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"
        assert self.user_id_2 in response.json()['bookshelf']["contributors"], "Contributor Added"

        # Get user_2s contributor bookshelves
        user_2_headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}
        response = requests.get(f"{self.endpoint}/api/bookshelves/contributed_bookshelves/{self.user_id_2}", headers=user_2_headers)
        assert response.status_code == 200, "Getting Contributed Bookshelves"
        assert len(response.json()['bookshelves']) == 1, "Getting Contributed Bookshelves"
        bookshelf = response.json()['bookshelves'][0]
        assert bookshelf["id"] == bookshelf_id, "Getting Contributed Bookshelves"

        # Add the same contributor again (duplicate)
        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/add_contributor", headers=headers, json=data)
        assert response.status_code == 200, "Adding Contributor"

        # Get the bookshelf again
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"
        assert len(response.json()['bookshelf']["contributors"]) == 2, "Duplicate Contributor Not Added"

        # Get the contributors of the bookshelf
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/contributors", headers=headers)
        assert response.status_code == 200, "Getting Contributors"
        assert len(response.json()['contributors']) == 2, "Getting Contributors"
        print(response.json()['contributors'])

        # Remove the contributor from the bookshelf
        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/remove_contributor", headers=headers, json=data)
        assert response.status_code == 200, "Removing Contributor"

        # Get the bookshelf again
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"
        assert self.user_id_2 not in response.json()['bookshelf']["contributors"], "Contributor Removed"

        # Delete the bookshelf
        response = requests.delete(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/delete", headers=headers)
        assert response.status_code == 200, "Deleting Bookshelf"
        
    def test_members(self):
        """
        Test case to test adding and removing members
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }

        # Create a bookshelf
        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"

        bookshelf_id = response.json()["bookshelf_id"]

        data = {
            "member_id": self.user_id_2
        }

        # Add a member to the bookshelf
        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/add_member", headers=headers, json=data)
        assert response.status_code == 200, "Adding member"

        # Get the bookshelf
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"
        assert self.user_id_2 in response.json()['bookshelf']["members"], "Member Added"

        # Get just the members
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/members", headers=headers)
        assert response.status_code == 200, "Getting Members"
        assert len(response.json()['members']) == 2, "Getting Members"
        print(response.json()['members'])

        # Get user_2s member bookshelves
        user_2_headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}
        response = requests.get(f"{self.endpoint}/api/bookshelves/member_bookshelves/{self.user_id_2}", headers=user_2_headers)
        assert response.status_code == 200, "Getting Member Bookshelves"
        assert len(response.json()['bookshelves']) == 1, "Getting Member Bookshelves"
        bookshelf = response.json()['bookshelves'][0]
        assert bookshelf["id"] == bookshelf_id, "Getting Member Bookshelves"

        # Try adding the same member again (duplicate member)
        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/add_member", headers=headers, json=data)
        assert response.status_code == 200, "Adding member"

        # Get the bookshelf again
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"
        assert len(response.json()['bookshelf']["members"]) == 1, "Duplicate member Not Added"

        # Remove the member from the bookshelf
        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/remove_member", headers=headers, json=data)
        assert response.status_code == 200, "Removing member"

        # Get the bookshelf again
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"
        assert self.user_id_2 not in response.json()['bookshelf']["members"], "Member Removed"

        # Delete the bookshelf
        response = requests.delete(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/delete", headers=headers)
        assert response.status_code == 200, "Deleting Bookshelf"

    def test_followers(self):
        """
        Test case to test adding and removing followers
        """
        headers = {"Authorization": f"{self.token_type} {self.access_token}"}
        data = {
            "bookshelf_name": "Test Bookshelf",
            "bookshelf_description": "Test Bookshelf Description",
            "visibility": "public"
        }

        # Create a bookshelf
        response = requests.post(f"{self.endpoint}/api/bookshelves/create", headers=headers, json=data)
        assert response.status_code == 200, "Creating Bookshelf"

        bookshelf_id = response.json()["bookshelf_id"]

        user_2_headers = {"Authorization": f"{self.token_type_2} {self.access_token_2}"}

        # Add a follower to the bookshelf
        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/follow", headers=user_2_headers)
        assert response.status_code == 200, "Adding follower"

        # Get the bookshelf
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=user_2_headers)
        assert response.status_code == 200, "Getting Bookshelf"
        assert response.json()['bookshelf']["follower_count"] == 1, "follower Added"

        # Get just the followers
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/followers", headers=user_2_headers)
        assert response.status_code == 200, "Getting followers"
        assert len(response.json()['followers']) == 1, "Getting followers"
        print(response.json()['followers'])

        # Unfollow
        response = requests.put(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/unfollow", headers=user_2_headers)
        assert response.status_code == 200, "Unfollowing"

        # Get the followers again
        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/followers", headers=user_2_headers)
        assert response.status_code == 200, "Getting followers"
        assert not response.json()['followers'], "Getting followers"

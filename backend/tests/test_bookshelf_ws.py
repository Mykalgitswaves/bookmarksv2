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

    yield

    response = requests.post(f"{request.cls.endpoint}/api/admin/delete_user_by_username", 
                             json={"username": request.cls.username, "admin_credentials": config["ADMIN_CREDENTIALS"]})

    assert response.status_code == 200, "Cleanup: Test user deletion failed"

@pytest.mark.usefixtures("setup_class")
class TestBookshelfWS:
    """
    Test class for Websocket operations on Bookshelves
    """
    def test_create_bookshelf(self):
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

        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"

        response = requests.delete(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/delete", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Deleting Bookshelf"

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """
        Test case to check the websocket connection to the bookshelf.
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

        response = requests.get(f"{self.endpoint}/api/bookshelves/{bookshelf_id}", headers=headers)
        assert response.status_code == 200, "Getting Bookshelf"

        uri = f"ws://127.0.0.1:8000/api/bookshelves/ws/{bookshelf_id}?token={self.access_token}"
        async with websockets.connect(uri) as ws:
            assert ws.open, "Websocket Connection"
            response = await ws.recv()
            ws_token = json.loads(response)['token']
            assert ws_token, "Websocket Token Not Received"

            small_img_url = "http://books.google.com/books/content?id=_uawAAAAIAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE732DLT-Q5P4M6ll9fpW5DH-Lz-FrGxwAQptgERj0vxnZYrLz57WvWzJ5k8Rr-OVQdQBOAImZNKuZQkgOgOO1HH2l5tUMj62Zngs0JbkXfsQIy3PcS_v8oHhB3XB7M0irmn4gM9g&source=gbs_api"
            # Prepare data to send to the server. Here we're sending JSON.
            data_to_send = {"type": "add", "token": ws_token, "book": {"title": "Second Foundation", 
                                                                       "small_img_url": small_img_url,
                                                                       "authors": ["Isaac Asimov"],
                                                                       "id": "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872"}}
            await ws.send(json.dumps(data_to_send))
            
            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response:", response_after_completion)

            await ws.send(json.dumps(data_to_send))
            
            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response on duplicate:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response on duplicate:", response_after_completion)

            data_to_send = {"type": "delete", "token": ws_token, "target_id": "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872"}

            await ws.send(json.dumps(data_to_send))
            
            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response on remove:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response on remove:", response_after_completion)

            data_to_send = {"type": "add", "token": ws_token, "book": {"title": "Second Foundation", 
                                                                       "small_img_url": small_img_url,
                                                                       "authors": ["Isaac Asimov"],
                                                                       "id": "c707fd781-dd1a-4ba7-91f1-f1a2e7ecb872"}}
            await ws.send(json.dumps(data_to_send))
            
            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response:", response_after_completion)

            small_img_url = "http://books.google.com/books/publisher/content?id=zJiJDQAAQBAJ&printsec=frontcover&img=1&zoom=5&edge=curl&imgtk=AFLRE7101pEA1qPqLGWj3HZGYk066aVnUx5od6ELqnAUw6y7YJyuaCg67i-feAewSsl9o0_ya__x6cl7HlnlEPLkxS1MtkyDzlgXO3s0KVRzcahD0_9gOYwFQPfJkqrQtUOdeffhxQSL&source=gbs_api"

            data_to_send = {"type": "add", "token": ws_token, "book": {"title": "What Are You Looking At?", 
                                                                       "small_img_url": small_img_url,
                                                                       "authors": ["Will Gompertz"],
                                                                       "id": "c5af309c7-3ac9-4d32-a7ce-32cbe818c15d"}}
            await ws.send(json.dumps(data_to_send))
            
            # Optionally, wait for another response after sending the data
            response_after_sending = await ws.recv()
            print("Server response:", response_after_sending)
            response_after_completion = await ws.recv()
            print("Server response:", response_after_completion)

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

        response = requests.delete(f"{self.endpoint}/api/bookshelves/{bookshelf_id}/delete", headers=headers)
        print(response.json())
        assert response.status_code == 200, "Deleting Bookshelf"
        
        

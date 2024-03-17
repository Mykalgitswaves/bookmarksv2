from fastapi.param_functions import Form
from pydantic import BaseModel

class SignUpForm:
    def __init__(
        self,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
    ):
        self.username = username
        self.email = email
        self.password = password

class LoginForm:
    def __init__(
        self,
        username: str = Form(None),
        email: str = Form(None),
        password: str = Form(...)
    ):
        self.username = username
        self.email = email
        self.password = password

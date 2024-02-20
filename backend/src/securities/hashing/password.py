from src.config.config import settings
from passlib.context import CryptContext

class PasswordGenerator:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=settings.JWT_SCHEMES, deprecated="auto")
    def generate_hashed_password(self, new_password: str) -> str:
        return self.pwd_context.hash(new_password)

    def is_password_authenticated(self, password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(password, hashed_password)


def get_pwd_generator() -> PasswordGenerator:
    return PasswordGenerator()


pwd_generator: PasswordGenerator = get_pwd_generator()
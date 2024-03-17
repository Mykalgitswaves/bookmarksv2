from src.config.config import settings

class GoogleBooks():
    def __init__(self) -> None:
        self.api_key = settings.GOOGLE_BOOKS_API_KEY
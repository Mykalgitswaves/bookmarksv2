import datetime

import pydantic
from jose import jwt as jose_jwt, JWTError as JoseJWTError
from fastapi.security import OAuth2PasswordBearer

from src.config.config import settings
from src.models.schemas.jwt import JWToken, JWTUser, JWTBookshelfWSUser
from src.models.schemas.users import User
from src.utils.exceptions.database import EntityDoesNotExist
from src.utils.logging.logger import logger


class JWTGenerator:
    def __init__(self):
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    def _generate_jwt_token(
        self,
        *,
        jwt_data: dict[str, str],
        expires_delta: datetime.timedelta | None = None,
    ) -> str:
        to_encode = jwt_data.copy()

        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta

        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.JWT_MIN_EXPIRE)

        to_encode.update(JWToken(exp=expire, sub=settings.JWT_SUBJECT).dict())

        return jose_jwt.encode(to_encode, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def generate_access_token(self, username: str) -> str:
        if not username:
            raise EntityDoesNotExist(f"Cannot generate JWT token for without User entity!")

        logger.info(
            "Access token being generated",
            extra={
                "username": username,
                "action": "generate_access_token",
            }
        )
        return self._generate_jwt_token(
            jwt_data=JWTUser(username=username).dict(),  # type: ignore
            expires_delta=datetime.timedelta(minutes=settings.JWT_MIN_EXPIRE),
        )

    def retrieve_details_from_token(self, token: str, secret_key: str) -> str:
        try:
            payload = jose_jwt.decode(token=token, key=secret_key, algorithms=[settings.JWT_ALGORITHM])
            jwt_user = JWTUser(username=payload["username"])

        except JoseJWTError as token_decode_error:
            logger.warning(
                "Unable to decode JWT Token",
                extra={
                    "token": token,
                    "action": "retrieve_details_from_token",
                }
            )
            raise ValueError("Unable to decode JWT Token") from token_decode_error

        except pydantic.ValidationError as validation_error:
            logger.warning(
                "Invalid payload in token",
                extra={
                    "token": token,
                    "action": "retrieve_details_from_token",
                }
            )
            raise ValueError("Invalid payload in token") from validation_error

        return jwt_user.username
    
    def _generate_bookshelf_websocket_token(
        self,
        *,
        jwt_data: dict[str, str],
        expires_delta: datetime.timedelta | None = None,
    ) -> str:
        to_encode = jwt_data.copy()

        if expires_delta:
            expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta

        else:
            expire =  datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.WS_MIN_EXPIRE)

        to_encode.update(JWToken(exp=expire, sub=settings.WS_SUBJECT).dict())

        return jose_jwt.encode(to_encode, key=settings.WS_SECRET_KEY, algorithm=settings.WS_ALGORITHM)

    def generate_bookshelf_websocket_token(self, user_id: str, bookshelf_id: str) -> str:
        if not user_id or not bookshelf_id:
            raise EntityDoesNotExist(f"Cannot generate JWT token for WS without User or bookshelf entity!")

        logger.info(
            "Bookshelf websocket token being generated",
            extra={
                "user_id": user_id,
                "bookshelf_id": bookshelf_id,
                "action": "generate_bookshelf_websocket_token",
            }
        )

        return self._generate_bookshelf_websocket_token(
            jwt_data=JWTBookshelfWSUser(id=user_id,
                                        bookshelf_id=bookshelf_id).dict(),  # type: ignore
            expires_delta=datetime.timedelta(minutes=settings.WS_MIN_EXPIRE),
        )

    def retrieve_details_from_bookshelf_ws_token(self, token: str, secret_key: str) -> str:
        try:
            payload = jose_jwt.decode(token=token, key=secret_key, algorithms=[settings.WS_ALGORITHM])
            ws_user = JWTBookshelfWSUser(id=payload["id"], bookshelf_id=payload["bookshelf_id"])

        except JoseJWTError:
            logger.warning(
                "Unable to decode JWT Token",
                extra={
                    "token": token,
                    "action": "retrieve_details_from_bookshelf_ws_token",
                }
            )
            return

        except pydantic.ValidationError:
            logger.warning(
                "Invalid payload in token",
                extra={
                    "token": token,
                    "action": "retrieve_details_from_bookshelf_ws_token",
                }
            )
            return

        return ws_user.id, ws_user.bookshelf_id

def get_jwt_generator() -> JWTGenerator:
    return JWTGenerator()


jwt_generator: JWTGenerator = get_jwt_generator()
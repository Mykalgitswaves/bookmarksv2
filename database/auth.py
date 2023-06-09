import json
from jose import jwt, JWTError

with open("config.json","r") as f:
    CONFIG = json.load(f)

def verify_access_token(access_token: str) -> bool:
    try:
        decoded_token = jwt.decode(access_token, CONFIG['SECRET_KEY'], algorithms=CONFIG['ALGORITHM'])
        return decoded_token
        print(decoded_token)
    except JWTError:
        # Handle JWT decoding error
        return None
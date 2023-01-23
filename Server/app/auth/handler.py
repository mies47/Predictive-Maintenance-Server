import jwt
import time
from typing import Dict


JWT_SECRET = 'thisisasecretkeyandhopeyoucantseeit' \
             'thisisasecretkeyandhopeyoucantseeit' \
             'thisisasecretkeyandhopeyoucantseeit' \
             'thisisasecretkeyandhopeyoucantseeit'
JWT_ALGORITHM = 'HS256'
HASH_METHOD = 'sha256'


def token_response(token: str):
    return {
        "access_token": token
    }


def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 900
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
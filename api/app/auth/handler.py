import jwt
import os
from typing import Dict
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_EXPIRES_IN_MINUTES = os.getenv('JWT_EXPIRES_IN_MINUTES')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')

HASH_ALGORITHM=os.getenv('HASH_ALGORITHM')


def token_response(token: str):
    return {
        'access_token': token
    }


def signJWT(key: str, value: str) -> Dict[str, str]:
    payload = {
        key: value,
        'exp': datetime.utcnow() + timedelta(minutes=float(JWT_EXPIRES_IN_MINUTES))
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
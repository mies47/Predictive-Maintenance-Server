import jwt
from typing import Dict
from datetime import datetime, timedelta

from ..utils.env_vars import JWT_SECRET, JWT_EXPIRES_IN_MINUTES, JWT_ALGORITHM


def signJWT(key: str, value: str) -> Dict[str, str]:
    payload = {
        key: value,
        'exp': datetime.utcnow() + timedelta(minutes=float(JWT_EXPIRES_IN_MINUTES))
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def decodeJWT(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
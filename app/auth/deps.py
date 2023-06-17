from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..postgresdb.postgres import SessionLocal
from ..postgresdb.models import Admin, Gateway

from .handler import decodeJWT

auth_scheme = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_admin(token: HTTPAuthorizationCredentials = Depends(auth_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    not_verified_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Admin is not verified yet',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decodeJWT(token=token.credentials)
        email: str = payload.get('email')
        if email is None:
            raise credentials_exception

    except:
        raise credentials_exception
    
    admin = db.query(Admin).filter(Admin.email == email).first() 
        
    if admin is None:
        raise credentials_exception
    
    if not admin.is_verified:
        raise not_verified_exception

    return admin


async def get_current_gateway(token: HTTPAuthorizationCredentials = Depends(auth_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    not_verified_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Gateway is not verified yet',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decodeJWT(token=token.credentials)
        mac: str = payload.get('mac')
        if mac is None:
            raise credentials_exception

    except:
        raise credentials_exception
    
    gateway = db.query(Gateway).filter(Gateway.mac == mac).first() 
        
    if gateway is None:
        raise credentials_exception


    if not gateway.is_verified:
        raise not_verified_exception

    return gateway
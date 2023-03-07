from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..influxdb.influx import InfluxDB
from ..postgresdb.postgres import SessionLocal
from ..postgresdb.models import Admin
from ..auth.handler import decodeJWT
from ..analytics.preprocess import Preprocess


router = APIRouter(
    prefix='/analytics',
    tags=['analytics'],
    responses={
        404: {'description': 'Not found'}
    }
)

db = SessionLocal()

influx = InfluxDB()

auth_scheme = HTTPBearer()


async def get_current_admin(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
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

    return admin


@router.post('/preprocess')
async def preprocess_all_data(admin = Depends(get_current_admin)):
    vibration_data = influx.get_vibration_data()

    preprocessor = Preprocess(vibration_data=vibration_data)
    preprocessor.start()


@router.post('/preprocess/{nodeId}')
async def preprocess_node_data(nodeId: str, admin = Depends(get_current_admin)):
    vibration_data = influx.get_vibration_data(nodeId=nodeId)
    
    preprocessor = Preprocess(vibration_data=vibration_data)
    preprocessor.start()
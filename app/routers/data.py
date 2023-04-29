from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..models.SendDataModel import DataModelList
from ..influxdb.influx import InfluxDB
from ..postgresdb.postgres import SessionLocal
from ..postgresdb.models import Gateway, Admin
from ..auth.handler import decodeJWT

from pydantic import parse_obj_as

import pandas as pd

router = APIRouter(
    prefix='/data',
    tags=['data'],
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


async def get_current_gateway(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
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

    return gateway


@router.get('/allData')
async def get_all_data(admin = Depends(get_current_admin)):
    result = influx.get_vibration_data()

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get('/nodeData/{nodeId}')
async def get_node_data(nodeId: str, admin = Depends(get_current_admin)):
    result = influx.get_vibration_data(nodeId=nodeId)

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get('/allNodes')
async def get_nodes_id(admin = Depends(get_current_admin)):
    result = influx.get_all_nodes_id()

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get('/allMeasurements')
async def get_measurments_id(admin = Depends(get_current_admin)):
    result = influx.get_all_measurements_id()

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.post('')
async def send_data(dataList: DataModelList, gateway = Depends(get_current_gateway)):
    dList = parse_obj_as(DataModelList, dataList)
    influx.write_vibration_data(data=dList)

    return JSONResponse(content='', status_code=status.HTTP_204_NO_CONTENT)
from typing import Dict

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from ..models.SendDataModel import NodeModel
from ..influxdb.influx import InfluxDB
from ..auth.deps import get_current_admin, get_current_gateway

from pydantic import parse_obj_as

import pandas as pd

router = APIRouter(
    prefix='/data',
    tags=['data'],
    responses={
        404: {'description': 'Not found'}
    }
)


influx = InfluxDB()


@router.get('')
async def get_all_data(admin = Depends(get_current_admin)):
    result = influx.get_vibration_data()

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get('/{nodeId}')
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
async def send_data(dataList: Dict[str, NodeModel], gateway = Depends(get_current_gateway)):
    dList = parse_obj_as(Dict[str, NodeModel], dataList)
    influx.write_vibration_data(data=dList)

    return JSONResponse(content='', status_code=status.HTTP_202_ACCEPTED)


@router.delete('')
async def delete_vibration_data(admin = Depends(get_current_admin)):
    influx.clear_vibration_data()
    
    return JSONResponse(content='Vibration data deleted successfully!', status_code=status.HTTP_200_OK)
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ..models.SendDataModel import DataModelList, DataModel, VibrationDataModel
from ..influxdb.influx import InfluxDB

from pydantic import parse_obj_as

import pandas as pd


router = APIRouter(
    prefix="/data",
    tags=["data"],
    responses={
        404: {"description": "Not found"}
    }
)

influx = InfluxDB()


@router.get("/")
async def get_all_data():
    result = influx.get_vibration_data()

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get("/{nodeId}")
async def get_node_data(nodeId: str):
    result = influx.get_vibration_data(nodeId=nodeId)

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.post(
    "/",
    responses={
        400: {'description': 'Bad request'}
    }
)
async def send_data(dataList: DataModelList):

    dList = parse_obj_as(DataModelList, dataList)
    for nodeData in dList.data:
        nData = parse_obj_as(DataModel, nodeData)
        for vibrationData in nData.vibrationData:
            vData = parse_obj_as(VibrationDataModel, vibrationData)
            influx.write_vibration_data(nodeId=nData.nodeId, data=vData)
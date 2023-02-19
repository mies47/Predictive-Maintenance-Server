from fastapi import APIRouter, HTTPException, Request
from ..models.SendDataModel import DataModelList, DataModel, VibrationDataModel
from ..influxdb.influx import InfluxDB
from pydantic import parse_obj_as


router = APIRouter(
    prefix="/data",
    tags=["data"],
    responses={
        404: {"description": "Not found"}
    }
)

influx = InfluxDB()

@router.get("/")
async def default_response():
    return {"response": "Data route is working!"}


@router.post(
    "/",
    responses={
        400: {'description': 'Bad request'}
    }
)
async def send_data(dataList: DataModelList):

    # dList = parse_obj_as(DataModelList, dataList)
    # for nodeData in dList.data:
    #     nData = parse_obj_as(DataModel, nodeData)
    #     for vibrationData in nData.vibrationData:
    #         vData = parse_obj_as(VibrationDataModel, vibrationData)
    #         influx.write_vibration_data(nodeId=nData.nodeId, data=vData)

    influx.get_all_vibration_data()
from fastapi import APIRouter, HTTPException, Request
from ..models.SendDataModel import DataModelList


router = APIRouter(
    prefix="/data",
    tags=["data"],
    responses={
        404: {"description": "Not found"}
    }
)


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
    print(dataList)
    # TODO: write data into the database
    for d in dataList:
        pass
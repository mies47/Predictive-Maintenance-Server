from pydantic import BaseModel
from typing import List


class VibrationDataModel(BaseModel):
    time: float
    measurementId: str
    x: float
    y: float
    z: float

    class Config:
        orm_mode = True


class DataModel(BaseModel):
    nodeId: str
    vibrationData: List[VibrationDataModel]

    class Config:
        orm_mode = True


class DataModelList(BaseModel):
    data: List[DataModel]

    class Config:
        orm_mode = True
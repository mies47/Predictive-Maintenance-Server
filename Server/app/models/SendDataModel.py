from pydantic import BaseModel
from typing import Dict, List


class VibrationDataModel(BaseModel):
    time: float
    x: float
    y: float
    z: float


class DataModel(BaseModel):
    nodeId: str
    vibrationData: List[VibrationDataModel]


class DataModelList(BaseModel):
    data: List[DataModel]
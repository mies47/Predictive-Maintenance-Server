from pydantic import BaseModel
from typing import List, Dict


class VibrationDataModel(BaseModel):
    x: float
    y: float
    z: float

    class Config:
        orm_mode = True


class MeasurementModel(BaseModel):
    id: str
    time: float
    data: List[VibrationDataModel]

    class Config:
        orm_mode = True


class NodeModel(BaseModel):
    node_id: str
    measurements: Dict[str, MeasurementModel]

    class Config:
        orm_mode = True
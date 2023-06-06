from pydantic import BaseModel


class GetDataModel(BaseModel):
    nodeId: str | None = None
    measurementId: str | None = None
from pydantic import BaseModel


class GatewayLoginModel(BaseModel):
    mac: str
    password: str


class AdminLoginModel(BaseModel):
    email: str
    password: str
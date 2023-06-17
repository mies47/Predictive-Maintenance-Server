from pydantic import BaseModel, EmailStr, Required
from fastapi import Query

from typing import Annotated


class GatewayLoginModel(BaseModel):
    mac: str = Required
    password: Annotated[str, Query(min_length = 5)] = Required
    
    class Config:
        orm_mode = True


class AdminLoginModel(BaseModel):
    email: EmailStr = Required
    password: Annotated[str, Query(min_length = 5)] = Required
    
    class Config:
        orm_mode = True
        

class GatewaySignupModel(GatewayLoginModel):
    pass


class AdminSignupModel(AdminLoginModel):
    name: Annotated[str, Query(min_length = 2)] = Required


class AdminOut(BaseModel):
    name: str
    email: EmailStr
    is_verified: bool

    class Config:
        orm_mode = True
        

class GatewayOut(BaseModel):
    mac: str
    is_verified: bool

    class Config:
        orm_mode = True
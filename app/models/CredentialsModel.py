from pydantic import BaseModel, EmailStr, Required
from fastapi import Query

from typing import Annotated


class GatewayLoginModel(BaseModel):
    mac: str = Required
    password: Annotated[str, Query(min_length = 8)] = Required
    
    class Config:
        orm_mode = True


class AdminLoginModel(BaseModel):
    email: EmailStr = Required
    password: Annotated[str, Query(min_length = 8)] = Required
    
    class Config:
        orm_mode = True
        

class GatewaySignupModel(GatewayLoginModel):
    pass


class AdminSignupModel(AdminLoginModel):
    name: Annotated[str, Query(min_length = 2)] = Required


class AdminOut(BaseModel):
    name: str
    email: EmailStr

    class Config:
        orm_mode = True
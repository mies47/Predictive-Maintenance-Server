from pydantic import BaseModel


class GatewayLoginModel(BaseModel):
    mac: str
    password: str
    
    class Config:
        orm_mode = True


class AdminLoginModel(BaseModel):
    email: str
    password: str
    
    class Config:
        orm_mode = True
        

class GatewaySignupModel(GatewayLoginModel):
    pass


class AdminSignupModel(AdminLoginModel):
    name: str


class AdminOut(BaseModel):
    name: str
    email: str

    class Config:
        orm_mode = True
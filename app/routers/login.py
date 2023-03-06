from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from werkzeug.security import check_password_hash

from ..models.CredentialsModel import AdminLoginModel, GatewayLoginModel
from ..postgresdb.postgres import SessionLocal
from ..postgresdb.models import Gateway, Admin
from ..auth.handler import signJWT


router = APIRouter(
    prefix='/login',
    tags=['login'],
    responses={404: {'description': 'Not found'}},
)

db = SessionLocal()


@router.post('/gateway')
async def gateway_login(loginModel: GatewayLoginModel):
    gateway = db.query(Gateway).filter(Gateway.mac == loginModel.mac).first()
    
    if not gateway:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail='Entered gateway does not exist or mac is incorrect')
    
    if check_password_hash(gateway.password, loginModel.password):
        return JSONResponse(status_code=status.HTTP_200_OK, 
                            content={'token': signJWT('mac', gateway.mac)})
      
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                         detail='Incorrect password')  
    
  

@router.post('/admin')
async def admin_login(loginModel: AdminLoginModel):
    admin = db.query(Admin).filter(Admin.email == loginModel.email).first()
    
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail='Entered admin does not exist or email is incorrect')
    
    if check_password_hash(admin.password, loginModel.password):
        return JSONResponse(status_code=status.HTTP_200_OK, 
                            content={'token': signJWT('email', admin.email)})
      
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                         detail='Incorrect password')  
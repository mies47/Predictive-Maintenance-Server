from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from ..models.CredentialsModel import AdminLoginModel, GatewayLoginModel
from ..postgresdb.models import Gateway, Admin
from ..auth.handler import signJWT
from ..auth.deps import get_db


router = APIRouter(
    prefix='/login',
    tags=['login'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/gateway')
async def gateway_login(loginModel: GatewayLoginModel, db: Session = Depends(get_db)):
    gateway = db.query(Gateway).filter(Gateway.mac == loginModel.mac).first()
    
    if not gateway:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail='Entered gateway does not exist or mac is incorrect')
    
    if check_password_hash(gateway.password, loginModel.password):

        gateway.login()
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, 
                            content={'token': signJWT('mac', gateway.mac)})
      
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                         detail='Incorrect password')  
    
  

@router.post('/admin')
async def admin_login(loginModel: AdminLoginModel, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == loginModel.email).first()
    
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail='Entered admin does not exist or email is incorrect')
    
    if check_password_hash(admin.password, loginModel.password):

        admin.login()
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, 
                            content={'token': signJWT('email', admin.email)})
      
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                         detail='Incorrect password')  
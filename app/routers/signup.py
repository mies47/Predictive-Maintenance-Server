from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from ..models.CredentialsModel import AdminSignupModel, GatewaySignupModel
from ..postgresdb.models import Gateway, Admin
from ..auth.handler import signJWT
from ..auth.deps import get_db
from ..utils.env_vars import HASH_ALGORITHM


router = APIRouter(
    prefix='/signup',
    tags=['signup'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/gateway')
async def gateway_signup(signupModel: GatewaySignupModel, db: Session = Depends(get_db)):
    gateway = db.query(Gateway).filter(Gateway.mac == signupModel.mac).first()
    
    if gateway:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                             detail='Entered gateway exists')
    
    new_gateway = Gateway(mac=signupModel.mac, 
                          password=generate_password_hash(signupModel.password, HASH_ALGORITHM))
    db.add(new_gateway)
    db.commit()
    
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={'token': signJWT('mac', new_gateway.mac)})
  

@router.post('/admin')
async def admin_signup(signupModel: AdminSignupModel, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == signupModel.email).first()
    
    if admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                             detail='Entered admin exists')
    
    new_admin = Admin(name=signupModel.name, 
                      email=signupModel.email,
                      password=generate_password_hash(signupModel.password, HASH_ALGORITHM))
    db.add(new_admin)
    db.commit()
    
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={'token': signJWT('email', new_admin.email)})
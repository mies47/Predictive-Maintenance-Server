from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from werkzeug.security import check_password_hash

from ..models.LoginModel import AdminLoginModel, GatewayLoginModel
from ..db.postgres import SessionLocal
from ..db.models import Gateway, Admin
from ..auth.handler import signJWT


router = APIRouter(
    prefix="/login",
    tags=["login"],
    responses={404: {"description": "Not found"}},
)

db = SessionLocal()


@router.get("/")
async def default_response():
    return {"response": "Credentials route is working!"}


@router.post("/gateway")
async def gateway_login(loginModel: GatewayLoginModel):
    gateway = db.query(Gateway).filter(Gateway.mac == loginModel.mac).first()
    
    if not gateway:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
                            content={'message': 'Entered gateway does not exist or mac is incorrect'})
    
    if check_password_hash(gateway.password, loginModel.password):
        return JSONResponse(status_code=status.HTTP_200_OK, 
                            content={'token': signJWT(gateway.mac)})
        
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, 
                        content={'message': 'Incorrect password'})
    
  

@router.post("/admin")
async def admin_login(loginModel: AdminLoginModel):
    admin = db.query(Admin).filter(Admin.email == loginModel.email).first()
    
    if not admin:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
                            content={'message': 'Entered admin does not exist or email is incorrect'})
    
    if check_password_hash(admin.password, loginModel.password):
        return JSONResponse(status_code=status.HTTP_200_OK, 
                            content={'token': signJWT(admin.email)})
        
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, 
                        content={'message': 'Incorrect password'})
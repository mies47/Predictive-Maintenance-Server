from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from werkzeug.security import generate_password_hash

from ..models.CredentialsModel import AdminSignupModel, GatewaySignupModel
from ..postgresdb.postgres import SessionLocal
from ..postgresdb.models import Gateway, Admin
from ..auth.handler import signJWT, HASH_ALGORITHM


router = APIRouter(
    prefix="/signup",
    tags=["signup"],
    responses={404: {"description": "Not found"}},
)

db = SessionLocal()


@router.get("/")
async def default_response():
    return {"response": "Sign up route is working!"}


@router.post("/gateway")
async def gateway_signup(signupModel: GatewaySignupModel):
    gateway = db.query(Gateway).filter(Gateway.mac == signupModel.mac).first()
    
    if gateway:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, 
                             detail='Entered gateway exists')
    
    new_gateway = Gateway(mac=signupModel.mac, 
                          password=generate_password_hash(signupModel.password, HASH_ALGORITHM))
    db.add(new_gateway)
    db.commit()
    
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={'token': signJWT('mac', new_gateway.mac)})
  

@router.post("/admin")
async def admin_signup(signupModel: AdminSignupModel):
    admin = db.query(Admin).filter(Admin.email == signupModel.email).first()
    
    if admin:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, 
                             detail='Entered admin exists')
    
    new_admin = Admin(name=signupModel.name, 
                      email=signupModel.email,
                      password=generate_password_hash(signupModel.password, HASH_ALGORITHM))
    db.add(new_admin)
    db.commit()
    
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={'token': signJWT('email', new_admin.email)})
from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..models.CredentialsModel import GatewayOut, AdminOut, GatewayVerificationModel
from ..auth.deps import get_current_admin, get_db
from ..postgresdb.models import Gateway


router = APIRouter(
    prefix='/gateway',
    tags=['gateway'],
    responses={404: {'description': 'Not found'}},
)


@router.get('/all', response_model=List[GatewayOut])
def all_gateways_info(admin: AdminOut = Depends(get_current_admin), db: Session = Depends(get_db)):
    gateways = list(db.query(Gateway))
    
    return gateways


@router.put('/verify')
def verify_admin(gatewayVerificationModel: GatewayVerificationModel, admin: AdminOut = Depends(get_current_admin), db: Session = Depends(get_db)):
    gateway_to_verify = db.query(Gateway).filter(Gateway.mac == gatewayVerificationModel.mac).first()
    
    if not gateway_to_verify:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail='Entered gateway does not exist or mac is incorrect')
        
    if gateway_to_verify.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                             detail='Entered gateway is already verified')
        
    gateway_to_verify.verify()
    db.commit()
    
    return JSONResponse(status_code=status.HTTP_200_OK, 
                            content={'detail': 'Gateway verified successfully'})
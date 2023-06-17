from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..models.CredentialsModel import AdminOut, AdminVerificationModel
from ..auth.deps import get_current_admin, get_db
from ..postgresdb.models import Admin


router = APIRouter(
    prefix='/admin',
    tags=['admin'],
    responses={404: {'description': 'Not found'}},
)


@router.get(
    '/me',
    response_model=AdminOut,
    status_code=status.HTTP_200_OK
)
def current_admin_info(admin: AdminOut = Depends(get_current_admin)):
    return admin


@router.get(
    '/all', 
    response_model=List[AdminOut], 
    status_code=status.HTTP_200_OK
)
def all_admins_info(admin: AdminOut = Depends(get_current_admin), db: Session = Depends(get_db)):
    admins = list(db.query(Admin))
    
    return admins


@router.put('/verify')
def verify_admin(adminVerificationModel: AdminVerificationModel, admin: AdminOut = Depends(get_current_admin), db: Session = Depends(get_db)):
    admin_to_verify = db.query(Admin).filter(Admin.email == adminVerificationModel.email).first()
    
    if not admin_to_verify:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail='Entered admin does not exist or email is incorrect')
        
    if admin_to_verify.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                             detail='Entered admin is already verified')
        
    admin_to_verify.is_verified = True
    db.commit()
    
    return JSONResponse(status_code=status.HTTP_200_OK, 
                            content={'detail': 'Admin verified successfully'})

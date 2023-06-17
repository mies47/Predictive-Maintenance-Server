from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.CredentialsModel import AdminOut
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


@router.get('/all', response_model=List[AdminOut])
def all_admins_info(admin: AdminOut = Depends(get_current_admin), db: Session = Depends(get_db)):
    if not admin.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin is not verified yet')

    admins = list(db.query(Admin))
    
    return admins

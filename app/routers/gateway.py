from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.CredentialsModel import GatewayOut, AdminOut
from ..auth.deps import get_current_admin, get_db
from ..postgresdb.models import Gateway


router = APIRouter(
    prefix='/gateway',
    tags=['gateway'],
    responses={404: {'description': 'Not found'}},
)


@router.get('/all', response_model=List[GatewayOut])
def all_gateways_info(admin: AdminOut = Depends(get_current_admin), db: Session = Depends(get_db)):
    if not admin.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin is not verified yet')

    gateways = list(db.query(Gateway))
    
    return gateways

from fastapi import APIRouter, status, Depends

from ..models.CredentialsModel import AdminOut

from app.deps import get_current_admin


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
def current_admin_info(
    admin: AdminOut = Depends(get_current_admin)
):
    return admin

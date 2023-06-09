from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..influxdb.influx import InfluxDB
from ..postgresdb.postgres import SessionLocal
from ..postgresdb.models import Admin
from ..auth.handler import decodeJWT
from ..analytics.transformer import Transformer
from ..analytics.preprocesser import Preprocesser


router = APIRouter(
    prefix='/analytics',
    tags=['analytics'],
    responses={
        404: {'description': 'Not found'}
    }
)

db = SessionLocal()

influx = InfluxDB()

auth_scheme = HTTPBearer()


async def get_current_admin(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decodeJWT(token=token.credentials)
        email: str = payload.get('email')
        if email is None:
            raise credentials_exception

    except:
        raise credentials_exception
    
    admin = db.query(Admin).filter(Admin.email == email).first() 
        
    if admin is None:
        raise credentials_exception

    return admin


@router.get('/rms')
async def get_rms_features(nodeId: str = None, measurementId: str = None, admin = Depends(get_current_admin)):
    
    rms_features = influx.get_rms_features(nodeId=nodeId, measurmentId=measurementId)
    if rms_features:
        return JSONResponse(content=rms_features, status_code=status.HTTP_200_OK)
    
    vibration_data = influx.get_vibration_data()
    nodes_ids = influx.get_all_nodes_id()
    measurements_ids = influx.get_all_measurements_id()

    transformer = Transformer(vibration_data=vibration_data)
    matrices = transformer.get_matrices()

    preprocessor = Preprocesser(matrices=matrices, nodes_ids=nodes_ids, measurements_ids=measurements_ids)  
    rms_features = preprocessor.rms_feature_extraction()
    
    influx.write_rms_features(rms_features=rms_features)
    
    return JSONResponse(content=rms_features, status_code=status.HTTP_200_OK)


@router.get('/psd')
async def get_psd_features(nodeId: str = None, measurementId: str = None, admin = Depends(get_current_admin)):
        
    psd_features = influx.get_psd_features(nodeId=nodeId, measurmentId=measurementId)
    if psd_features:
        return JSONResponse(content=psd_features, status_code=status.HTTP_200_OK)
    
    vibration_data = influx.get_vibration_data()
    nodes_ids = influx.get_all_nodes_id()
    measurements_ids = influx.get_all_measurements_id()

    transformer = Transformer(vibration_data=vibration_data)
    matrices = transformer.get_matrices()

    preprocessor = Preprocesser(matrices=matrices, nodes_ids=nodes_ids, measurements_ids=measurements_ids)  
    psd_features = preprocessor.psd_feature_extraction()
    
    influx.write_psd_features(psd_features=psd_features)
    
    return JSONResponse(content=psd_features, status_code=status.HTTP_200_OK)


@router.get('/peaks')
async def get_harmonic_peaks(nodeId: str = None, measurementId: str = None, admin = Depends(get_current_admin)):
    
    harmonic_peaks = influx.get_harmonic_peaks(nodeId=nodeId, measurmentId=measurementId)
    if harmonic_peaks:
        return JSONResponse(content=harmonic_peaks, status_code=status.HTTP_200_OK)
    
    vibration_data = influx.get_vibration_data()
    nodes_ids = influx.get_all_nodes_id()
    measurements_ids = influx.get_all_measurements_id()

    transformer = Transformer(vibration_data=vibration_data)
    matrices = transformer.get_matrices()

    preprocessor = Preprocesser(matrices=matrices, nodes_ids=nodes_ids, measurements_ids=measurements_ids)  
    harmonic_peaks = preprocessor.harmonic_peak_feature_extraction()
    
    influx.write_harmonic_peaks(harmonic_peaks=harmonic_peaks)
    
    return JSONResponse(content=harmonic_peaks, status_code=status.HTTP_200_OK)


@router.delete('/cachedData')
async def delete_cached_processed_data(admin = Depends(get_current_admin)):
    influx.clear_cached_data()
    
    return JSONResponse(content='Cached data deleted successfully!', status_code=status.HTTP_200_OK)
from fastapi import FastAPI

from .utils.env_vars import API_PREFIX
from .utils.constants import MACHINE_LABELS


def create_database():
    from .postgresdb.postgres import Base, engine
    from .postgresdb.postgres import SessionLocal
    from .postgresdb.models import Admin, Gateway, MachineClass

    Base.metadata.create_all(engine)

    db = SessionLocal()

    if db.query(MachineClass).first() is None:
        labels = [MachineClass(string=string, description=description) for string, description in MACHINE_LABELS.items()]
    
        db.add_all(labels)
        db.commit()


def clear_time_series_database():
    from .influxdb.influx import InfluxDB

    influx = InfluxDB()
    influx.clear_database()


def initialize_server():
    from .routers import admin, data, login, signup, analytics
    
    app = FastAPI()
    
    app.include_router(admin.router, prefix=API_PREFIX)
    app.include_router(data.router, prefix=API_PREFIX)
    app.include_router(login.router, prefix=API_PREFIX)
    app.include_router(signup.router, prefix=API_PREFIX)
    app.include_router(analytics.router, prefix=API_PREFIX)
    
    create_database()


    '''Uncomment this line when you want to make influxdb empty'''
    # clear_time_series_database()
    
    return app

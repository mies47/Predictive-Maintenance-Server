from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


def initialize_server():
    from .routers import admin, data, login, signup, analytics
    
    app = FastAPI()

    origins = [
        "http://localhost",
        "http://localhost:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(admin.router, prefix=API_PREFIX)
    app.include_router(data.router, prefix=API_PREFIX)
    app.include_router(login.router, prefix=API_PREFIX)
    app.include_router(signup.router, prefix=API_PREFIX)
    app.include_router(analytics.router, prefix=API_PREFIX)
    
    create_database()
    
    return app

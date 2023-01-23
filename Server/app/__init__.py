from fastapi import FastAPI


API_V1 = '/api/v1'


def create_database():
    from .db.postgres import Base, engine
    from .db.models import Admin, Gateway

    Base.metadata.create_all(engine)


def initialize_server():
    from .routers import data, login
    
    app = FastAPI()
    
    app.include_router(data.router, prefix=API_V1)
    app.include_router(login.router, prefix=API_V1)
    
    # create_database()
    
    return app
    
    
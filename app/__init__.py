from fastapi import FastAPI

from .utils.env_vars import API_PREFIX


def create_database():
    from .postgresdb.postgres import Base, engine
    from .postgresdb.models import Admin, Gateway

    Base.metadata.create_all(engine)


def initialize_server():
    from .routers import data, login, signup, analytics
    
    app = FastAPI()
    
    app.include_router(data.router, prefix=API_PREFIX)
    app.include_router(login.router, prefix=API_PREFIX)
    app.include_router(signup.router, prefix=API_PREFIX)
    app.include_router(analytics.router, prefix=API_PREFIX)
    
    create_database()
    
    return app

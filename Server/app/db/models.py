from sqlalchemy.sql.expression import null
from .postgres import Base
from sqlalchemy import String, Integer, Column


class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=True)


    def __repr__(self):
        return f"<Admin email={self.email} password={self.password}>"


class Gateway(Base):
    __tablename__ = 'gateways'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mac = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False, unique=True)


    def __repr__(self):
        return f"<Gateway mac={self.mac} password={self.password}>"
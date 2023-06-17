from sqlalchemy import String, Integer, Column, Boolean

from .postgres import Base


class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    is_verified = Column(Boolean, nullable=True, default=False)


    def __repr__(self):
        return f'<Admin email={self.email} password={self.password}>'


class Gateway(Base):
    __tablename__ = 'gateways'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mac = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False, unique=True)
    is_verified = Column(Boolean, nullable=True, default=False)


    def __repr__(self):
        return f'<Gateway mac={self.mac} password={self.password}>'
    

class MachineClass(Base):
    __tablename__ = 'machineClasses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    string = Column(String(2), nullable=False, unique=True)
    description = Column(String(255), nullable=False, unique=True)


    def __repr__(self):
        return f'<Machine Class {self.string}: {self.description}>'

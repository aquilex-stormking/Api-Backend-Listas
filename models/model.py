from sqlalchemy import Column, Integer, String, Date
from utils.connection import Base
from jose import jwt

class Listas(Base):
    __tablename__ = 'listas'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    listofac= Column(String(1))
    listonu= Column(String(1))
    listfbi= Column(String(1))
    finddate= Column(Date)
    consulta= Column(String(5))
    user=Column(String(50))

class User(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    password= Column(String(100))
    email= Column(String(50))
    createdate= Column(Date)
    state=Column(String(1))
    rol= Column(String(50))
    identificacion = Column(Integer)
    nit = Column(Integer)

class Match(Base):
    __tablename__ = 'match'
    
    id = Column(Integer, primary_key=True)
    observacion= Column(String(100))
    resultado= Column(String(50))
    fecha= Column(Date)
    usuario=Column(String(50))
    consulta = Column(String(100))

class Listas_add(Base):
    __tablename__ = 'listas_add'
    
    id = Column(Integer, primary_key=True)
    descripcion= Column(String(100))
    fecha= Column(Date)
        



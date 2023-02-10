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

class User(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    password= Column(String(100))
    email= Column(String(50))
    createdate= Column(Date)



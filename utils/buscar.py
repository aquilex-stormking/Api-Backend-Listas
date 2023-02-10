import jaro 
import warnings
from sqlalchemy import create_engine, Column, BIGINT, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
def buscar(persona):

    dbUID="sa"
    dbPWD="1213"
    dbSERVER="DESKTOP-T6B6RV0"
    dbNAME="LISTAS_RESTRITIVAS"
    dbPORT="1433"
    warnings.filterwarnings("ignore")

    engine = create_engine(f'mssql+pymssql://{dbUID}:{dbPWD}@{dbSERVER}:{dbPORT}/{dbNAME}')

    Session = sessionmaker(engine)
    session = Session()

    Base = declarative_base()

    class ListOfac(Base):
        __tablename__ = 'ListOfac'
        
        index = Column(BIGINT,primary_key=True)
        uid = Column(String(max))
        first_name = Column(String(max))
        
        def serialize(self):
            return {
                "index": self.index,
                "uid": self.uid,
                "first_name": self.first_name
            }

    class ListOnu(Base):
        __tablename__ = 'ListOnu'
        
        index = Column(BIGINT,primary_key=True)
        dataid = Column(String(max))
        first_name = Column(String(max))
        
        def serialize(self):
            return {
                "index": self.index,
                "dataid": self.dataid,
                "first_name": self.first_name
            }

    class ListFbi(Base):
        __tablename__ = 'ListFbi'
        
        index = Column(BIGINT,primary_key=True)
        uid = Column(String(max))
        title = Column(String(max))
        
        def serialize(self):
            return {
                "index": self.index,
                "uid": self.uid,
                "title": self.title
            }
        
    persona_en_Ofac =session.query(ListOfac.first_name).all()
    persona_en_Onu =session.query(ListOnu.first_name).all()
    persona_en_Fbi = session.query(ListFbi.title).all()
    nombre_busca= persona
    valOfac=' '
    valOnu=' '
    valFbi=' '

    for persona in persona_en_Ofac:
        persona=str(persona)
        p= jaro.jaro_metric(nombre_busca,persona)
        if p>=0.77 :
            valOfac='X'

    for persona in persona_en_Onu:
        persona=str(persona)
        p= jaro.jaro_metric(nombre_busca,persona)
        if p>=0.77 :
            valOnu='X'


    for persona in persona_en_Fbi:
        persona=str(persona)
        p= jaro.jaro_metric(nombre_busca,persona)
        if p>=0.77 :
            valFbi='X'

    lista ={'persona':nombre_busca,'listOfac':valOfac,'listOnu':valOnu,'listFbi':valFbi}

    print(lista)
    return lista
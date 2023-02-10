import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
import warnings
from sqlalchemy import create_engine



# libreria para ignorar las advertencias
def traeDatos(page=1):
        response = requests.get('https://api.fbi.gov/wanted/v1/list', params={
        'page': page
    })
        data = json.loads(response.content)
        return  data

def cargardatos():

    dbUID="sa"
    dbPWD="1213"
    dbSERVER="DESKTOP-T6B6RV0"
    dbNAME="LISTAS_RESTRITIVAS"
    dbPORT="1433"
    warnings.filterwarnings("ignore")
    engine = create_engine(f'mssql+pymssql://{dbUID}:{dbPWD}@{dbSERVER}:{dbPORT}/{dbNAME}')


    #Obtener Datos de XML   
    # Se obtiene la informacion de la ofac
    urlofac = "https://www.treasury.gov/ofac/downloads/consolidated/consolidated.xml"
    xmlofac = requests.get(urlofac)
    soupofac = BeautifulSoup(xmlofac.content, 'lxml', from_encoding='utf-8')
    persona = soupofac.findAll('sdnentry')
    pasa1 = []
    for i in persona:
        fName = i.find('firstname')
        sName= i.find('lastname')
        uID=i.find('uid')
        if fName is not None and sName is not None :
            pasa1.append((uID.text,(fName.text+" "+sName.text).upper()))
        if fName is not None:
            pasa1.append((uID.text,(fName.text).upper()))
        if sName is not None:
            pasa1.append((uID.text,(sName.text).upper()))

    dfofac = pd.DataFrame(pasa1, columns=['uid', 'first_name'])
    dfofac.to_sql('ListOfac',engine, if_exists='replace')

    # Se obtiene la informacion de la onu
    url = "https://scsanctions.un.org/resources/xml/sp/consolidated.xml"
    xml = requests.get(url)
    soup = BeautifulSoup(xml.content, 'lxml', from_encoding='utf-8')
    persona = soup.findAll('individual')
    pasa1 = []

    for i in persona:
        dataId= i.find('dataid')
        fName= i.find('first_name')
        sName= i.find('second_name')
        tName= i.find('third_name')
        aName= i.find('alias_name')
        if fName is not None and sName is not None and tName is not None and aName is not None:
            nombre = fName.text+' '+sName.text+' '+tName.text+' '+aName.text
            pasa1.append((dataId.text,nombre.upper()))
        if fName is not None and sName is not None and tName is not None:
            nombre = fName.text+' '+sName.text+' '+tName.text
            pasa1.append((dataId.text,nombre.upper()))
        if fName is not None and sName is not None and aName is not None:
            nombre = fName.text+' '+sName.text+' '+aName.text
            pasa1.append((dataId.text,nombre.upper()))
            
    dfonu = pd.DataFrame(pasa1, columns=['dataid', 'first_name'])
    #almacenar datos en la base de datos sql
    dfonu.to_sql('ListOnu',engine, if_exists='replace')

    #Se obtiene la informacion del fbi
    
    data=traeDatos()
    datos = data['total']
    dato = 0
    guarda = []
    page=0
    while dato < datos:
        
        data=traeDatos(page)
        
        for o in data['items']:
            
            if o['title'] is not None and o['uid'] is not None:
                guarda.append((o['uid'],o['title']))
            dato+=1
        page+=1
    dffbi = pd.DataFrame(guarda, columns=['uid', 'title'])
    dffbi.to_sql('ListFbi',engine, if_exists='replace')

cargardatos()
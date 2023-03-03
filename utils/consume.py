import requests
from fastapi import Depends
import jaro
from datetime import date
from .procesar_archivo import buscar2
import random,string
import pandas as pd
import app
from .config import get_settings

dato=get_settings()

def consumir(nombre_busca):
    
    valOfac=' '
    valOnu=' '
    valFbi=' '
    nombre_busca=nombre_busca.upper()
    nombre_busca=nombre_busca.replace(" ", "")

    #Ofac
    url = dato.URLOFAC
    data = requests.get(url)
    if data.status_code == 200:
        dataOfac= data.json()
    for datos in dataOfac :
        datos=str(datos[1])
        p= jaro.jaro_metric(nombre_busca,datos)
        if p>=0.77 :
            valOfac='X'
    #Onu
    url =dato.URLONU
    data = requests.get(url)
    if data.status_code == 200:
        dataOnu= data.json()
    for datos in dataOnu:
        datos=str(datos[1])
        p= jaro.jaro_metric(nombre_busca,datos)
        if p>=0.77 :
            valOnu='X'
    
    url =dato.URLFBI
    data = requests.get(url)
    if data.status_code == 200:
        dataFbi= data.json()
    for datos in dataFbi:
        datos=str(datos[1])
        datos = datos
        p= jaro.jaro_metric(nombre_busca,datos)
        if p>=0.77 :
            valFbi='X'


    #Generador de id de consulta
    rand = random.choice(string.ascii_letters)
    rand1 = random.choice(string.ascii_letters)
    rand2 = random.randint(1, 20) * 5
    rand = rand1+str(rand2)+rand
    today = str(date.today())

    lista ={'FirstName':nombre_busca,'ListOfac':valOfac,'ListOnu':valOnu,'ListFbi':valFbi,'FindDate':today,'Consulta':rand}
    
    return lista

def consumir2(lista:list,name:str):

    lista1 = {'Nombre':[],'ListaOnu':[],'ListaOfac':[],'ListaFBI':[],'ListaCargue':[]}
    writer=pd.ExcelWriter(dato.NAME_ARCHIVO_REPORTE)
    for nombre_busca in lista:
        if nombre_busca[0] is not None:

            valOfac=' '
            valOnu=' '
            valFbi=' '
            nombre_busca=nombre_busca[0].upper()
            valCargue=buscar2(nombre_busca)
            
            #Ofac
            url =dato.URLOFAC
            data = requests.get(url)
            if data.status_code == 200:
                dataOfac= data.json()
            for datos in dataOfac :
                datos=str(datos)
                p= jaro.jaro_metric(nombre_busca,datos)
                if p>=0.77 :
                    valOfac='X'
            #Onu
            url =dato.URLONU
            data = requests.get(url)
            if data.status_code == 200:
                dataOnu= data.json()
            for datos in dataOnu:
                datos=str(datos)
                p= jaro.jaro_metric(nombre_busca,datos)
                if p>=0.77 :
                    valOnu='X'
            
            url =dato.URLFBI
            data = requests.get(url)
            if data.status_code == 200:
                dataFbi= data.json()
            for datos in dataFbi:
                datos=str(datos)
                p= jaro.jaro_metric(nombre_busca,datos)
                if p>=0.77 :
                    valOnu='X'

            #añadir a lista
            lista1['Nombre'].append(nombre_busca)
            lista1['ListaOfac'].append(valOfac)
            lista1['ListaOnu'].append(valOnu)
            lista1['ListaFBI'].append(valFbi)
            lista1['ListaCargue'].append(valCargue)
    
    df1=pd.DataFrame(lista1, columns=['Nombre','ListaOfac','ListaOnu','ListaFBI','ListaCargue'])
    df1.to_excel(writer,'Reporte',index=False)
    writer.save()
    

    #Generador de id de consulta
    rand = random.choice(string.ascii_letters)
    rand1 = random.choice(string.ascii_letters)
    rand2 = random.randint(1, 20) * 5
    rand = rand1+str(rand2)+rand
    today = str(date.today())

    lista ={'FirstName':name,'ListOfac':'','ListOnu':'','ListFbi':'','FindDate':today,'Consulta':rand}
    
    return lista
    
    


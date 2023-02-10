import requests
import jaro
from datetime import date
import random,string
def consumir(nombre_busca):
    
    valOfac=' '
    valOnu=' '
    valFbi=' '
    nombre_busca=nombre_busca

    #Ofac
    url ='http://127.0.0.1:8080/ListaOfac'
    data = requests.get(url)
    if data.status_code == 200:
        dataOfac= data.json()
    for datos in dataOfac :
        datos=str(datos)
        p= jaro.jaro_metric(nombre_busca,datos)
        if p>=0.77 :
            valOfac='X'
    #Onu
    url ='http://127.0.0.1:8080/ListaOnu'
    data = requests.get(url)
    if data.status_code == 200:
        dataOnu= data.json()
    for datos in dataOnu:
        datos=str(datos)
        p= jaro.jaro_metric(nombre_busca,datos)
        if p>=0.77 :
            valOnu='X'
    
    url ='http://127.0.0.1:8080/ListaFbi'
    data = requests.get(url)
    if data.status_code == 200:
        dataFbi= data.json()
    for datos in dataFbi:
        datos=str(datos)
        p= jaro.jaro_metric(nombre_busca,datos)
        if p>=0.77 :
            valOnu='X'
    #Generador de id de consulta
    rand = random.choice(string.ascii_letters)
    rand1 = random.choice(string.ascii_letters)
    rand2 = random.randint(1, 20) * 5
    rand = rand1+str(rand2)+rand
    today = str(date.today())

    lista ={'FirstName':nombre_busca,'ListOfac':valOfac,'ListOnu':valOnu,'ListFbi':valFbi,'FindDate':today,'Consulta':rand}
    
    return lista


import pandas as pd
from os import getcwd, mkdir, path, rename
from PIL import Image
import jaro

def crearlista():
    existe= path.exists("dummy5.pkl")
    if not existe:
        lista = []
        nombre_completo = ''
        identificacion = ''
        tipo_identificacion = ''
        direccion = ''
        ciudad = ''
        pais = ''
        link_photo = ''
        lista.append((nombre_completo,identificacion,tipo_identificacion,direccion,ciudad,pais,link_photo))
        dfperson = pd.DataFrame(lista, columns = ['nombre_completo', 'identificacion','tipo_identificacion','direccion','ciudad','pais','link_photo'])
        dfperson.to_pickle("dummy5.pkl")
    
    existe= path.exists("./photos")
    if not existe:
        mkdir("./photos")

def add_person(nombre_completo, identificacion,tipo_identificacion,direccion,ciudad,pais,link_photo,empresa):
    df = pd.read_pickle('dummy5.pkl')
    df['nombre_completo'] = nombre_completo.upper()
    df['identificacion'] = identificacion
    df['tipo_identificacion'] = tipo_identificacion
    df['direccion'] = direccion
    df['ciudad'] = ciudad
    df['pais'] = pais
    df['link_photo'] = link_photo
    df['empresa'] = empresa
    df.to_pickle('dummy5.pkl')

def leerlistaperson():
    datosperson = pd.read_pickle("dummy5.pkl")

    lista=[]
    lista = datosperson.to_numpy().tolist()
    
    return lista 

def buscarlistaperson(nombre_busca,coincidencia):
    coincidencia = coincidencia/100
    datosperson = pd.read_pickle("dummy5.pkl")
    nombre_busca = nombre_busca.upper()
    lista=[]
    lista = datosperson.to_numpy().tolist()
    listfind = []
    for datos in lista:
        nombre=str(datos[0])
        p= jaro.jaro_metric(nombre_busca,nombre)
        if p>=coincidencia :
            
            dicc_find = {'nombre_completo':datos[0],'identificacion':datos[1],'tipo_identificacion':datos[2],'direccion':datos[3],'ciudad':datos[4],'pais':datos[5],'link_photo':datos[6]}
            listfind.append(dicc_find)
    
    return listfind
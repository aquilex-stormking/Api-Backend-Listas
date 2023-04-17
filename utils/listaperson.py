import pandas as pd
from os import getcwd, mkdir, path, rename
from PIL import Image

def crearlista():
    existe= path.exists("dummy.pkl")
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
        dfperson.to_pickle("dummy.pkl")
    
    existe= path.exists("./photos")
    if not existe:
        mkdir("./photos")

def añadirperson(nombre_completo, identificacion,tipo_identificacion,direccion,ciudad,pais,link_photo):
    df = pd.read_pickle('dummy.pkl')
    df['nombre_completo'] = nombre_completo
    df['identificacion'] = identificacion
    df['tipo_identificacion'] = tipo_identificacion
    df['direccion'] = direccion
    df['ciudad'] = ciudad
    df['pais'] = pais
    df['link_photo'] = link_photo
    
    df.to_pickle('dummy.pkl')
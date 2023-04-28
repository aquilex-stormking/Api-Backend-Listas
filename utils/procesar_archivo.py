import openpyxl
import pandas as pd
import jaro
from utils import consume


url ="./files/"
url2 ="./files2/"
url3 = './files/dummy.pkl'
url4 = "./files2/dummy.pkl"

def comprobar2(name:str):
    book= openpyxl.load_workbook(url2+name, data_only=True)
    hoja = book.active
    celdas = hoja['A2':'A10']
    lista_cargue = []
    for fila in celdas:
        empleado = [celda.value for celda in fila]
        empleado= str(empleado[0])
        empleado = empleado.upper()
        if empleado !='NONE':
            lista_cargue.append(empleado)
    dcargue= pd.DataFrame(lista_cargue, columns=['first_name'])
    #almacenar datos en la base de datos sql
    dcargue.to_pickle(url4)
    datos = pd.read_pickle(url4) 
    lista = datos.to_numpy().tolist()
    lista1 = consume.consumir_2(lista,name)
    return lista1


def buscar2(name:str,coincidencia:int):
    coincidencia = coincidencia/100
    try:
        files = open(url3)
        files.close()    
        datos = pd.read_pickle(url3) 
        lista = datos.to_numpy().tolist()
        name = name.upper()
        val=''
        for datos in lista :
            datos = str(datos)
            p= jaro.jaro_metric(name,datos)
            if p >= coincidencia :
                val='x'
    
    except FileNotFoundError:
        val=''  
    return val


def comprobar(name:str):
    book= openpyxl.load_workbook(url+name, data_only=True)
    hoja = book.active
    celdas = hoja['A2':'A1000']
    lista_cargue = []
    for fila in celdas:
        empleado = [celda.value for celda in fila]
        empleado= str(empleado[0])
        empleado = empleado.upper()
        lista_cargue.append(empleado)
    dcargue= pd.DataFrame(lista_cargue, columns=['first_name'])
    #almacenar datos en la base de datos sql
    dcargue.to_pickle(url3)

#
def buscar(name:str):
    datos = pd.read_pickle(url3) 
    lista1=[]
    lista = datos.to_numpy().tolist()
    name = name.upper()
    val=False
    for datos in lista :
        datos=str(datos)
        p= jaro.jaro_metric(name,datos)
        if p>=0.88 :
            val=True
    lista1.append(val)
    return lista1
    


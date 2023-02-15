import openpyxl
import pandas as pd
import jaro
from utils import consume


url="./files/"
url2="./files2/"

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
    dcargue.to_pickle("./files2/dummy.pkl")
    datos = pd.read_pickle("./files2/dummy.pkl") 
    lista = datos.to_numpy().tolist()
    consume.consumir2(lista,name)



def buscar2(name:str):
    datos = pd.read_pickle("./files/dummy.pkl") 
    lista = datos.to_numpy().tolist()
    name = name.upper()
    val=''
    for datos in lista :
        datos=str(datos)
        p= jaro.jaro_metric(name,datos)
        if p>=0.88 :
            val='x'
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
    dcargue.to_pickle("./files/dummy.pkl")

#
def buscar(name:str):
    datos = pd.read_pickle("./files/dummy.pkl") 
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
    


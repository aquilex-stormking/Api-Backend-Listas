import requests
from fastapi import Depends
import jaro
from datetime import date
from .procesar_archivo import buscar2_id,buscar2_nombre
import random,string
import pandas as pd
from .config import get_settings
from fpdf import FPDF
import random
import string
import hashlib

dato=get_settings()

def generar_password(longitud):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choices(caracteres, k=longitud))
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash

def consumir(nombre_busca,coincidencia):
    
    coincidencia = coincidencia/100
    list_ofac = [] 
    list_onu = []
    list_fbi = []
    val_ofac = ' '
    val_onu = ' '
    val_fbi = ' '
    nombre_busca = nombre_busca.upper()
    nombre_busca = nombre_busca.replace(" ", "")

    #Ofac
    url = dato.URLOFAC
    data = requests.get(url)
    if data.status_code == 200:
        data_ofac = data.json()
    for datos in data_ofac :
        nombre = str(datos[1])
        p = jaro.jaro_metric(nombre_busca,nombre)
        if p >= coincidencia :
            val_ofac = 'X'
            dicc_onu = {'List':'Ofac','Name': datos[1] ,'tipoId':datos[2],'identificacion':datos[3],'direccion':datos[4],'pais':datos[5],'ciudad':datos[6]}
            list_ofac.append(dicc_onu)
            
            
    #Onu
    url =dato.URLONU
    data = requests.get(url)
    if data.status_code == 200:
        data_onu= data.json()
    for datos in data_onu:
        nombre=str(datos[1])
        p= jaro.jaro_metric(nombre_busca,nombre)
        if p>=coincidencia :
            val_onu='X'
            dicc_onu = {'List':'Onu','Name':datos[1],'Tipo_documento':datos[2],'Numero_documento':datos[3],'Description':datos[4],'Pais':datos[5],'Fecha_nacimiento':datos[6]}
            list_onu.append(dicc_onu)

    
    url =dato.URLFBI
    try:
        data = requests.get(url)
        if data.status_code == 200:
            data_fbi= data.json()
        for datos in data_fbi:
            nombre=str(datos[1])
            p= jaro.jaro_metric(nombre_busca,nombre)
            if p>=0.77 :
                val_fbi='X'
                dicc_fbi = {'List':'Fbi','name':datos[1],'Detalle':datos[2],'Link_info':datos[3],'Nacionalidad':datos[4],'Link_picture':datos[5],'Link_ref':datos[6]}
                list_fbi.append(dicc_fbi)
    except:
        raise Exception


    # Generador de id de consulta
    today = str(date.today())
    rand = generar_password(4)
    rand = rand[:5]
    lista_busquedad = list_onu + list_ofac + list_fbi

    lista ={'FirstName':nombre_busca,'ListOfac':val_ofac,'ListOnu':val_onu,'ListFbi':val_fbi,'FindDate':today,'Consulta':rand,'list_find':lista_busquedad}
    # lista = {}
    return lista

def consumir_id(id,coincidencia):
    coincidencia = coincidencia/100
    list_ofac = [] 
    list_onu = []
    list_fbi = []
    val_ofac = ' '
    val_onu = ' '
    val_fbi = ' '

    #Ofac
    url = dato.URLOFAC
    data = requests.get(url)
    if data.status_code == 200:
        data_ofac = data.json()
    for datos in data_ofac :
        nombre = str(datos[3])
        p = jaro.jaro_metric(id,nombre)
        if p >= coincidencia :
            val_ofac = 'X'
            dicc_onu = {'list':'Ofac','name': datos[1] ,'tipoId':datos[2],'identificacion':datos[3],'direccion':datos[4],'pais':datos[5],'ciudad':datos[6]}
            list_ofac.append(dicc_onu)
            
            
    #Onu
    url =dato.URLONU
    data = requests.get(url)
    if data.status_code == 200:
        data_onu= data.json()
    for datos in data_onu:
        nombre=str(datos[3])
        p= jaro.jaro_metric(id,nombre)
        if p>=coincidencia :
            val_onu='X'
            dicc_onu = {'list':'Onu','name':datos[1],'tipo_documento':datos[2],'numero_documento':datos[3],'description':datos[4],'pais':datos[5],'fecha_nacimiento':datos[6]}
            list_onu.append(dicc_onu)

    url =dato.URLFBI
    try:
        data = requests.get(url)
        if data.status_code == 200:
            data_fbi= data.json()
        for datos in data_fbi:
            nombre=str(datos[1])
            p= jaro.jaro_metric(id,nombre)
            if p>=coincidencia :
                val_fbi='X'
                dicc_fbi = {'list':'Fbi','name':datos[1],'detalle':datos[2],'link_info':datos[3],'nacionalidad':datos[4],'link_picture':datos[5],'link_ref':datos[6]}
                list_fbi.append(dicc_fbi)
    except:
        raise Exception

    #Generador de id de consulta
    
    rand = generar_password(8)
    rand = rand[:5]
    today = str(date.today())
    lista_busquedad = list_onu + list_ofac + list_fbi

    lista ={'FirstName':id,'ListOfac':val_ofac,'ListOnu':val_onu,'ListFbi':val_fbi,'FindDate':today,'Consulta':rand,'list_find':lista_busquedad}
    
    return lista

def consumir_2(lista:list,name:str):

    lista1 = {'Nombre':[],'ListaOnu':[],'ListaOfac':[],'ListaFBI':[],'ListaCargue':[]}
    writer=pd.ExcelWriter(dato.NAME_ARCHIVO_REPORTE)
    for nombre_busca in lista:
            
            val_ofac= ' '
            val_onu = ' '
            val_fbi = ' '
            id_busca = nombre_busca[0]
            nombre_busca=nombre_busca[1].upper()
            val_cargue=buscar2_id(nombre_busca,90)
            if val_cargue =='':
                val_cargue=buscar2_nombre(nombre_busca,90)
            
            #Ofac
            url =dato.URLOFAC
            data = requests.get(url)
            if data.status_code == 200:
                data_ofac= data.json()
            for datos in data_ofac :
                identificacion = str(datos[3])
                p= jaro.jaro_metric(id_busca,identificacion)
                if p>= 0.9 :
                    val_ofac='X'
                if val_ofac == ' ':
                    nombre = str(datos[1])
                    p= jaro.jaro_metric(nombre_busca,nombre)
                    if p>= 0.9 :
                        val_ofac='X'

            #Onu
            url =dato.URLONU
            data = requests.get(url)
            if data.status_code == 200:
                data_onu= data.json()
            for datos in data_onu:
                identificacion = str(datos[3])
                p= jaro.jaro_metric(id_busca,identificacion)
                if p>= 0.9 :
                    val_onu='X'
                if val_onu == ' ':
                    nombre = str(datos[1])
                    p= jaro.jaro_metric(nombre_busca,nombre)
                    if p>= 0.9 :
                        val_onu='X'
            
            url =dato.URLFBI
            data = requests.get(url)
            if data.status_code == 200:
                data_fbi= data.json()
            for datos in data_fbi:
                datos=str(datos)
                p= jaro.jaro_metric(nombre_busca,datos)
                if p>=0.9 :
                    val_onu='X'

            #añadir a lista
            lista1['Nombre'].append(nombre_busca)
            lista1['ListaOfac'].append(val_ofac)
            lista1['ListaOnu'].append(val_onu)
            lista1['ListaFBI'].append(val_fbi)
            lista1['ListaCargue'].append(val_cargue)
    
    df1=pd.DataFrame(lista1, columns=['Nombre','ListaOfac','ListaOnu','ListaFBI','ListaCargue'])
    
    pdf=FPDF()
    pdf.add_page()
    pdf.set_font("Arial",size=18)
    pdf.image("Imagen3.jpg", x=5, y=5, w=25, h=15)
    pdf.cell(0, 10, "Mi Reporte LPR", align="C")
    pdf.ln(20)
    pdf.image("7.jpg", x=180, y=5, w=20, h=20)
    pdf.ln(60)

    # Cabecera de la tabla
    pdf.set_font("Arial",size=12)
    r,g,b=52, 152, 219
    pdf.cell(20)
    pdf.set_fill_color(r,g,b)
    pdf.cell(40,10,"Nombre", border=1, align="C",fill=True)
    pdf.set_fill_color(r,g,b)
    pdf.cell(30,10,"Lista Ofac", border=1,align="C",fill=True)
    pdf.set_fill_color(r,g,b)
    pdf.cell(30,10,"Lista Onu", border=1,align="C",fill=True)
    pdf.set_fill_color(r,g,b)
    pdf.cell(30,10,"Lista FBI", border=1,align="C",fill=True)
    pdf.set_fill_color(r,g,b)
    pdf.cell(30,10,"Lista Cargue", border=1,align="C",fill=True)
    pdf.ln()

    # Agregar filas
    pdf.set_font("Arial",size=8)
    for fila in df1.values:
        pdf.cell(20)
        i=0
        for valor in fila:

            if i ==0:
                
                pdf.cell(40,10,str(valor), border=1, align="J")
            else :
                
                pdf.cell(30,10,str(valor), border=1,align="C")
            i+=1   
        pdf.ln()

    # Guardar archivo
    pdf.output("tabla.pdf")
    
    
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


def reportepdf(nombre_busca,coincidencia,listaofac,listaonu,listafbi):

    lista=[]
    today = str(date.today())
    lista.append((nombre_busca,listaofac,listaonu,listafbi))
    df1=pd.DataFrame(lista, columns=['Nombre','ListaOfac','ListaOnu','ListaFBI'])
    coincidencia = coincidencia

    #pdf
    pdf=FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica",size=24)
    pdf.image("Imagen3.jpg", x=5, y=5, w=25, h=15)
    pdf.cell(0, 10, "Mi Reporte LPR", align="C")
    pdf.ln(20)
    pdf.image("7.jpg", x=180, y=5, w=20, h=20)
    pdf.ln(20)
    pdf.set_font("Times",size=12)
    r,g,b=52, 152, 219
    pdf.cell(30)
    pdf.set_fill_color(r,g,b)
    pdf.cell(50,10,"Nombre", border=1, align="C",fill=True)
    pdf.set_fill_color(r,g,b)
    pdf.cell(30,10,"Lista Ofac", border=1,align="C",fill=True)
    pdf.set_fill_color(r,g,b)
    pdf.cell(30,10,"Lista Onu", border=1,align="C",fill=True)
    pdf.set_fill_color(r,g,b)
    pdf.cell(30,10,"Lista FBI", border=1,align="C",fill=True)
    pdf.set_fill_color(r,g,b)

    # Agregar filas
    pdf.set_font("Times",size=8)
    pdf.ln(10)       
    pdf.cell(30)
    pdf.cell(50,10,str(nombre_busca), border=1, align="J")  
    pdf.cell(30,10,str(listaofac), border=1,align="C")
    pdf.cell(30,10,str(listaonu), border=1,align="C")
    pdf.cell(30,10,str(listafbi), border=1,align="C")  
    pdf.ln(20)

    pdf.set_font("Times", size=14)
    pdf.cell(20)
    pdf.cell(0, 10, "La persona o entidad llamada: "+nombre_busca+" fue consulatada con  "+str(coincidencia)+" % de coincidencia ", align="J")
    pdf.ln(10)
    pdf.cell(20)
    pdf.cell(0, 10, "en la fecha "+today+" en las siguientes listas: Lista Ofac, Lista Onu, Lista FBI.", align="J")
    pdf.ln(10)
    # Cabecera de la tabla
    

    # Guardar archivo
    pdf.output("tabla2.pdf")
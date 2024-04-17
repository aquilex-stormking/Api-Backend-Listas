import requests
from fastapi import Depends
import jaro
from datetime import date
from .procesar_archivo import buscar2_id,buscar2_nombre,buscar
import random,string
import pandas as pd
from .config import get_settings
from fpdf import FPDF
import random
import string
import hashlib
import json
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
    lists =""
    ofac = 0
    onu = 0
    fbi = 0
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
            val_ofac = 'Ofac'
            if ofac == 0 :
                lists = lists + val_ofac
                ofac = 1
            dicc_onu = {'List':'Ofac','Name': datos[1] ,'TipoId':datos[2],'Identificacion':datos[3],'Direccion':datos[4],'Pais':datos[5],'Ciudad':datos[6]}
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
            val_onu='Onu'
            if onu == 0 :
                if ofac ==0:
                    lists =lists+ val_onu
                    onu = 1
                else :
                    lists =lists + ", " +val_onu
                    onu = 1
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
                val_fbi='Fbi'
                if fbi == 0 :
                    if ofac == 0 and onu == 0 :
                        lists =lists +val_fbi
                    else :
                        lists =lists + ", " +val_fbi
                        fbi = 1
                dicc_fbi = {'List':'Fbi','name':datos[1],'Detalle':datos[2],'Link_info':datos[3],'Nacionalidad':datos[4],'Link_picture':datos[5],'Link_ref':datos[6]}
                list_fbi.append(dicc_fbi)
    except:
        raise Exception


    # Generador de id de consulta
    today = str(date.today())
    rand = generar_password(4)
    rand = rand[:5]
    lista_busquedad = list_onu + list_ofac + list_fbi

    lista ={'FirstName':nombre_busca,'Listas':lists,'ListOfac':val_ofac,'ListOnu':val_onu,'ListFbi':val_fbi,'FindDate':today,'Consulta':rand,'list_find':lista_busquedad}
    # lista = {}
    return lista

def consumir_id(id,coincidencia):
    coincidencia = coincidencia/100
    list_ofac = [] 
    list_onu = []
    list_fbi = []
    lists =""
    ofac = 0
    onu = 0
    fbi = 0
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
            val_ofac = 'Ofac'
            if ofac == 0 :
                lists = lists + val_ofac
                ofac = 1
            dicc_onu = {'List':'Ofac','name': datos[1] ,'TipoId':datos[2],'Identificacion':datos[3],'Direccion':datos[4],'Pais':datos[5],'Ciudad':datos[6]}
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
            val_onu='Onu'
            if onu == 0 :
                if ofac ==0:
                    lists =lists+ val_onu
                    onu = 1
                else :
                    lists =lists + ", " +val_onu
                    onu = 1
            dicc_onu = {'list':'Onu','Name':datos[1],'Tipo_documento':datos[2],'Numero_documento':datos[3],'Description':datos[4],'Pais':datos[5],'Fecha_nacimiento':datos[6]}
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
                val_fbi='Fbi'
                if fbi == 0 :
                    if ofac == 0 and onu == 0 :
                        lists =lists +val_fbi
                    else :
                        lists =lists + ", " +val_fbi
                        fbi = 1
                dicc_fbi = {'list':'Fbi','Name':datos[1],'Detalle':datos[2],'Link_info':datos[3],'Nacionalidad':datos[4],'Link_picture':datos[5],'Link_ref':datos[6]}
                list_fbi.append(dicc_fbi)
    except:
        raise Exception

    #Generador de id de consulta
    
    rand = generar_password(8)
    rand = rand[:5]
    today = str(date.today())
    lista_busquedad = list_onu + list_ofac + list_fbi

    lista ={'FirstName':id,'Listas':lists,'ListOfac':val_ofac,'ListOnu':val_onu,'ListFbi':val_fbi,'FindDate':today,'Consulta':rand,'list_find':lista_busquedad}
    
    return lista

def fit_text(self, width, height, text):
        font_size = 8
        while self.get_string_width(text) > width and font_size > 2:
            self.set_font("Arial", size=font_size)
            font_size -= 0.1
        return font_size

def consumir_2(lista:list,name:str,coincidencia=None,lists=None):

    ancho = False
    if not coincidencia:
        # Añade los datos por defecto
        coincidencia = 70
    if not lists:
        lists=[]
    
    lista1 = []
    writer=pd.ExcelWriter(dato.NAME_ARCHIVO_REPORTE)
    for nombre_busca in lista:
            
            val_ofac= False
            val_onu = False
            val_fbi = False
            nivel = coincidencia
            id_busca = nombre_busca[0]
            nombre_busca=nombre_busca[1].upper()
            comprueba1= buscar(nombre_busca, coincidencia, lists)
            comprueba2= buscar(id_busca, coincidencia, lists)
            cadena1 = ''.join(comprueba1)
            cadena2 = ''.join(comprueba2)
            cadena = cadena1 + ", " + cadena2
            cant_carac = len(cadena)
            if cant_carac > 22 :
                ancho =True
            val_cargue = buscar2_id(nombre_busca,90)
            if val_cargue =='':
                val_cargue=buscar2_nombre(nombre_busca,90)
            
            coinci = coincidencia/100
            #Ofac
            url =dato.URLOFAC
            data = requests.get(url)

            if data.status_code == 200:
                data_ofac= data.json()
            for datos in data_ofac :
                identificacion = str(datos[3])
                p= jaro.jaro_metric(id_busca,identificacion)
                if p>= coinci :
                    val_ofac = True
                if val_ofac == ' ':
                    nombre = str(datos[1])
                    p= jaro.jaro_metric(nombre_busca,nombre)
                    if p>= coinci :
                        val_ofac = True
                    

            #Onu
            url =dato.URLONU
            data = requests.get(url)
            if data.status_code == 200:
                data_onu= data.json()
            for datos in data_onu:
                identificacion = str(datos[3])
                p= jaro.jaro_metric(id_busca,identificacion)
                if p>= coinci :
                    val_onu = True
                if val_onu == ' ':
                    nombre = str(datos[1])
                    p= jaro.jaro_metric(nombre_busca,nombre)
                    if p>= coinci :
                        val_onu = True
                    

            url =dato.URLFBI
            data = requests.get(url)
            if data.status_code == 200:
                data_fbi= data.json()
            for datos in data_fbi:
                datos=str(datos)
                p= jaro.jaro_metric(nombre_busca,datos)
                if p>= coinci :
                    val_fbi = True
                

            #añadir a lista
            item = {
                'Nombre': nombre_busca,
                'ListaOfac': val_ofac,
                'ListaOnu': val_onu,
                'ListaFBI': val_fbi,
                'Lista_Coincide': cadena,
                'Nivel_Coincidencia': nivel
            }
            lista1.append(item)
            # lista1['Nombre'].append(nombre_busca)
            # lista1['ListaOfac'].append(val_ofac)
            # lista1['ListaOnu'].append(val_onu)
            # lista1['ListaFBI'].append(val_fbi)
            # lista1['Lista_Coincide'].append(cadena)
            # lista1['Nivel_Coincidencia'].append(nivel)
   
    # nombre_archivo = "mi_dataframe.xlsx"
    # df1 = pd.DataFrame(lista1, columns=['Nombre','ListaOfac','ListaOnu','ListaFBI','Lista_Coincide','Nivel_Coincidencia'])
    # df1 = df1.to_json(orient='records')
    
    # pdf=FPDF()
    # pdf.encoding = 'cp1252'  # Cambia la codificación a 'utf-8' o 'cp1252'
    # pdf.add_page()
    # pdf.set_font("Arial",size=18)
    # pdf.image("Imagen3.jpg", x=5, y=5, w=25, h=15)
    # pdf.cell(0, 10, "Mi Reporte LPR", align="C")
    # pdf.ln(20)
    # pdf.image("7.jpg", x=180, y=5, w=20, h=20)
    # pdf.ln(60)

    # # Cabecera de la tabla
    # pdf.set_font("Arial",size=12)
    # r,g,b=52, 152, 219
    # pdf.cell(20)
    # pdf.set_fill_color(r,g,b)
    # pdf.cell(40,10,"Nombre", border=1, align="C",fill=True)
    # pdf.set_fill_color(r,g,b)
    # pdf.cell(30,10,"Lista Ofac", border=1,align="C",fill=True)
    # pdf.set_fill_color(r,g,b)
    # pdf.cell(30,10,"Lista Onu", border=1,align="C",fill=True)
    # pdf.set_fill_color(r,g,b)
    # pdf.cell(30,10,"Lista FBI", border=1,align="C",fill=True)
    # pdf.set_fill_color(r,g,b)
    # pdf.cell(30,10,"Lista Cargue", border=1,align="C",fill=True)
    # pdf.ln()

    
    # # Agregar filas
    # pdf.set_font("Arial",size=8)
    # for fila in df1.values:
    #     pdf.cell(20)
    #     i=0
    #     for valor in fila:

    #         if i == 0:
    #             pdf.set_font("Arial",size=8)
    #             pdf.cell(40, 30, valor, border=1, align="J")

    #         else :
    #             width = 30
    #             height = 30
    #             text = valor
    #             long_cad = len(valor)
    #             if long_cad >22:
                    
    #                 font_size = fit_text(pdf,width,height,text)
    #                 pdf.set_font("Arial", size=font_size)
    #                 valor = valor.encode('latin-1').decode('latin-1')
    #                 pdf.cell(30, 30, str(valor), border=1, align="J")
    #             else:     
    #                 valor = valor.encode('latin-1').decode('latin-1')
    #                 pdf.cell(30, 30, str(valor), border=1, align="J")     
                
    #         i+=1   
    #     pdf.ln()
    
    # # Guardar archivo
    # # pdf.output("tabla.pdf")
    
    
    # df1.to_excel(writer,'Reporte',index=False)
    # writer.save()
    

    #Generador de id de consulta
    rand = random.choice(string.ascii_letters)
    rand1 = random.choice(string.ascii_letters)
    rand2 = random.randint(1, 20) * 5
    rand = rand1+str(rand2)+rand
    today = str(date.today())

    lista ={'FirstName':name,'ListOfac':'','ListOnu':'','ListFbi':'','FindDate':today,'Consulta':rand}
    
    return lista1


def reportepdf(nombre_busca,coincidencia,lists):

    lista=[]
    today = str(date.today())
    lista.append((nombre_busca,lists))
    
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
    pdf.cell(30,10,"Listas", border=1,align="C",fill=True)
    pdf.set_fill_color(r,g,b)
    

    # Agregar filas
    pdf.set_font("Times",size=8)
    pdf.ln(10)       
    pdf.cell(30)
    pdf.cell(50,10,str(nombre_busca), border=1, align="J")  
    pdf.cell(30,10,str(lists), border=1,align="C")
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
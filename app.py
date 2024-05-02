import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Response
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from utils import connection,consume as con,procesar_archivo,sendmail, listaperson
from utils.config import Settings, get_settings
from models import schema
from models import model
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext 
from datetime import datetime, timedelta, date
from jose import jwt, JWTError
from os import getcwd, mkdir, path, rename
import shutil
import pandas as pd
from PIL import Image
import requests
import schedule
import time, json

#algorimo 
ALGORITHM="HS256"
ACCESS_TOKEN_DURATION = 60
SECRET = "761c78b692385bd23194ea3848b266589f4c4f16e245b0c7a977c29741bee075"

app = FastAPI()

listaperson.crearlista()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
dato = get_settings()
crypt = CryptContext(schemes=[dato.ENCRYPT])
    
oauth2 = OAuth2PasswordBearer(tokenUrl="login")


#Retorna autenticacion si es valida
async def auth_user(token: str = Depends(oauth2)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception

    return True
    
    

#Busca el usuario en la base de datos
def search_user_db(username:str, lists: list):
    for email in lists:    
        if username == email.email:
            return email
    return False

#Busca la contraseña del usuario
def search_password_db(lists:list,pos:str, passw:str):
    
    for password in lists:   
        if password.id == pos and password.password ==passw : 
            return passw


#GET
#consulta en las listas y devuelve lista
@app.get("/Consume/{nombre_busca}/{users}/{coincidencia}")
async def Consume(nombre_busca:str,users:str,coincidencia:int,db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    busqueda = con.consumir(nombre_busca,coincidencia) 
    new_list = model.Listas(firstname = busqueda['FirstName']
                            , listofac = busqueda['ListOfac']
                            , listonu = busqueda['ListOnu']
                            , listfbi = busqueda['ListFbi']
                            , finddate = busqueda['FindDate']
                            , consulta = busqueda['Consulta']
                            , user = users
                            )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    lista = {'FirstName':busqueda['FirstName'],'Listas':busqueda['Listas'],'FindDate':busqueda['FindDate'],'Consulta':busqueda['Consulta'],'list_find':busqueda['list_find']}
    return lista

#GET
#consulta en las listas y devuelve lista
@app.get("/Consumes/{id}/{users}/{coincidencia}")
async def consume(id:str,users:str,coincidencia:int,db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):

    busqueda=con.consumir_id(id,coincidencia) 
    
    new_list = model.Listas(firstname = busqueda['FirstName']
                            , listofac = busqueda['ListOfac']
                            , listonu = busqueda['ListOnu']
                            , listfbi = busqueda['ListFbi']
                            , finddate = busqueda['FindDate']
                            , consulta = busqueda['Consulta']
                            , user = users
                            )
    db.add(new_list)
    db.commit()
    db.refresh(new_list) 
    lista = {'FirstName':busqueda['FirstName'],'Listas':busqueda['Listas'],'FindDate':busqueda['FindDate'],'Consulta':busqueda['Consulta'],'list_find':busqueda['list_find']}
    return lista
    

#GET
#Obtiene todos las busquedas
@app.get("/Busquedas", response_model=List[schema.PersonFound])
async def get_all_busquedas(db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    query = db.query(model.Listas)
    query = query.order_by(desc(model.Listas.finddate))
    lists = query.all()
    return lists
#GET
#Obtiene todos las busquedas por usuario
@app.get("/Busqueda/{User}")
async def get_single_2(user:str, db: Session = Depends(connection.get_db),db1: Session =Depends(auth_user)):
    lista= []
    # get the patient with the given Patient ID
    query = db.query(model.Listas).filter(model.Listas.user == user).all()
    lista = query

    if not lista:
        raise HTTPException(status_code=404, detail=f"User{user} not found")

    return lista

#GET
#Obtiene todos los usuarios
@app.get("/User", response_model=List[schema.UserFound])
async def get_all(db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    query = db.query(model.User)
    lists = query.all()
    return lists

#GET
#Obtiene el usuario por id
@app.get("/User/{id}")
async def get_single(id: int, db: Session = Depends(connection.get_db),db1: Session =Depends(auth_user)):

    ids =id
    
    query = db.query(model.User).filter(model.User.id == ids)
    user = query.one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {id} not found")

    return user

#GET
#Obtiene todos los matchs
@app.get("/Matchs", response_model=List[schema.MatchFound])
async def get_all_1(db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    query = db.query(model.Match)
    query = query.order_by(desc(model.Match.fecha))
    lists = query.all()
    return lists



# POST
#Crea usuarios
@app.post("/User", response_model=schema.UserFound)
async def post(user_found: schema.UserFoundCreate, db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    
    myctx = CryptContext(schemes=[dato.ENCRYPT])
    user_found.password =myctx.hash(user_found.password)
    
    new_list2 = model.User(  firstname = user_found.firstname
                            ,password = user_found.password
                            ,email= user_found.email
                            ,createdate = user_found.createdate
                            ,state = user_found.state
                            ,rol = user_found.rol
                            ,nit=user_found.nit
                            ,identificacion=user_found.identificacion
                            )
    db.add(new_list2)
    db.commit()    
    # Actualiza base de datos
    db.refresh(new_list2) 
    # retorna lista
    return new_list2

# POST
#Crea usuarios
@app.post("/User2", response_model=schema.UserFound)
async def post_2(user_found: schema.UserFoundCreate, db: Session = Depends(connection.get_db)):
    
    myctx = CryptContext(schemes=[dato.ENCRYPT])
    user_found.password =myctx.hash(user_found.password)
    
    new_list2 = model.User(  firstname = user_found.firstname
                            ,password = user_found.password
                            ,email= user_found.email
                            ,createdate = user_found.createdate
                            ,state = user_found.state
                            ,rol = user_found.rol
                            ,nit=user_found.nit
                            ,identificacion=user_found.identificacion
                            )
    db.add(new_list2)
    db.commit()    
    # Actualiza base de datos
    db.refresh(new_list2) 
    # retorna lista
    return new_list2

# POST
#Crea usuarios
@app.post("/Match", response_model=schema.MatchFound)
async def post(match_found: schema.MatchFoundCreate, db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    
    
    new_list2 = model.Match( consulta = match_found.consulta
                            ,observacion = match_found.observacion
                            ,resultado = match_found.resultado
                            ,fecha = match_found.fecha
                            ,usuario = match_found.usuario
                            )
    db.add(new_list2)
    db.commit()    
    # Actualiza base de datos
    db.refresh(new_list2) 
    # retorna lista
    return new_list2

# PUT
#Edita a los usuarios
@app.put("/User/{ID}", response_model=schema.UserFound)
async def put(id: int, lists_update:schema.UserFound, db: Session = Depends(connection.get_db),  db1: Session =Depends(auth_user)):
    
    lists = db.get(model.User, id) 
    myctx = CryptContext(schemes=[dato.ENCRYPT])
    lists_update.password = myctx.hash(lists_update.password)
    if lists:
        lists.firstname = lists_update.firstname
        lists.password = lists_update.password
        lists.email = lists_update.email
        lists.state = lists_update.state
        lists.rol = lists_update.rol
        db.commit()
        db.refresh(lists)

    if not lists:
        raise HTTPException(status_code=404, detail=f"lists with ID {id} not found")

    return lists

# PUT
#Edita a los usuarios
@app.put("/Userdelete/{ID}", response_model=schema.UserFound)
async def put(id: int, db: Session = Depends(connection.get_db),  db1: Session =Depends(auth_user)):
    
    lists = db.get(model.User, id) 
    if lists:

        if lists.state == '1':
            lists.state='0'
        else:
            lists.state='1'
        db.commit()
        db.refresh(lists)

    if not lists:
        raise HTTPException(status_code=404, detail=f"lists with ID {id} not found")

    return lists    

# DELETE
#Elimina Usuarios
@app.delete("/User/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int,  db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    user = db.get(model.User, id)
    if user:
        db.delete(user)
        db.commit()

#POST
#logea al usuario
@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(connection.get_db)):
    prueba = await get_all(db)    

    user_db = search_user_db(form.username,prueba)
    
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")
    if not crypt.verify(form.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")
    if user_db.state=='0':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")
    if user_db is True:
        user_db=form.username
    acess_token = {"sub":form.username,"name":user_db.firstname,"rol":user_db.rol,"identificacion":user_db.identificacion,"nit":user_db.nit,"exp": datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_DURATION)}
    
    return {"access_token": jwt.encode(acess_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

#POST
#Caga lista personalizada
@app.post("/upload")
async def uploadfile(file:UploadFile =File(...),  db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    existe= path.exists("files")
    if existe:
        await delete_file("files")
        mkdir("files")
    else :
        mkdir("files")
    with open(getcwd()+"/files/"+ file.filename, "wb") as myfile:
        content = await file.read()
        myfile.write(content)
        myfile.close()
        os.rename('files/'+file.filename,'files/'+settings.NAME_ARCHIVO_CARGUE)
        procesar_archivo.comprobar(settings.NAME_ARCHIVO_CARGUE)
    return "success"

#POST
#Caga lista personalizada
@app.post("/upload2" ,tags=['Upload'])
async def uploadfile_2(file:UploadFile =File(...),settings: Settings = Depends(get_settings),db: Session = Depends(connection.get_db)):
    
    existe= path.exists("files")
    if not existe:
        mkdir("files")
    
    with open(getcwd()+"/files/"+ file.filename, "wb") as myfile:
        content = await file.read()
        myfile.write(content)
        myfile.close()
        today = str(date.today())
        os.rename('files/'+file.filename,'files/'+file.filename)
        name = procesar_archivo.comprobar(file.filename)
        registros = name['registros']
        print(registros)
        name = name['nombre']
        if registros > 281000 :
            result = f"excedes el total de resgistros permitidos estas cargando {registros} registros lo permitido son: 281000 "
        else:
            existing_item = db.query(model.Listas_add).filter(model.Listas_add.descripcion == name).first()
            if existing_item:
                existing_item.fecha = today   
                db.commit()
                lista = db.query(model.Registros).filter(model.Registros.descripcion == name).first()
                lista.registros = registros
                lista.fecha = today
                db.commit()
                result = "cargue actualizado exitosamente"
            else:
                new_list2 = model.Listas_add( descripcion = name
                                ,fecha = today
                                ,fecha_ant = today
                                )
                db.add(new_list2)
                db.commit()    
                # Actualiza base de datos
                # db.refresh(new_list2) 
                ultimo_id = db.query(model.Registros.id).order_by(desc(model.Registros.id)).first()
                ultimo_id = ultimo_id[0] +1
                new_list = model.Registros( id = ultimo_id,
                                            descripcion = name,
                                            registros = registros,
                                            fecha = today
                                        )
                db.add(new_list)
                db.commit()
                db.refresh(new_list)
                result = "cargue subido exitosamente"

    return result


#GET
#Obtiene lista individual de personas añadidas
@app.get("/Userban/{nit}")
async def get_person(nit:int, db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    lista = listaperson.leerlistaperson(nit)
    return lista

#POST
#Carga usuario individual 
@app.post("/Userban/{nombre}/{identificacion}/{tipo_identificacion}/{direccion}/{ciudad}/{pais}/{empresa}")
async def uploadfile(nombre:str, identificacion:str, tipo_identificacion:str, direccion:str,ciudad:str,pais:str,empresa:int,file:UploadFile =File(...),db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    link_photo = "/photos/"+ file.filename
    with open(getcwd()+"/photos/"+ file.filename, "wb") as myfile:
        content = await file.read()
        myfile.write(content)
        myfile.close()
    
    listaperson.add_person(nombre,identificacion,tipo_identificacion,direccion,ciudad,pais,link_photo,empresa)
    return True

#POST
#Carga usuario individual 
@app.post("/Userban/{nombre_busca}/{coincidencia}")
async def find_person(nombre_busca:str, coincidencia:int,db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    lista = listaperson.buscarlistaperson(nombre_busca,coincidencia)
    print(lista)
    # ruta_imagen = getcwd()+lista[0]['link_photo']
    # imagen = Image.open(ruta_imagen)

    return lista

#DELETE
#Elimina lista
@app.delete("/delete")
async def delete_file(folder_name:str,  db1: Session =Depends(auth_user)):
        shutil.rmtree(getcwd() +"/" + folder_name)
        return JSONResponse(content={
            "removed": True,}
            ,status_code=200)

#GET
#Busca en lista personalizada
@app.get("/findcharge/{name}/{coincidencia}")
async def findcharge(name:str, coincidencia:int , db1: Session =Depends(auth_user),db: Session = Depends(connection.get_db)):
    query = db.query(model.Listas_add)
    query = query.order_by(desc(model.Listas_add.fecha))
    lists = query.all()
    comprueba= procesar_archivo.buscar(name, coincidencia, lists)
    return comprueba

#GET
#Descarga lista cargada
@app.get("/downloadcharge/{name}")
async def downloadcharge(name:str,  db1: Session =Depends(auth_user), settings: Settings = Depends(get_settings)):
    file_path = path.join(path.abspath(getcwd()), "files", name)
    return FileResponse(file_path)

#POST
#Realiza busqueda por cargue de archivo cruzando todas las listas y envial  al correo
@app.post("/uploadMassive/{email}/{users}",tags=["Upload"])
async def uploadfilemassive(email:str,users:str,file:UploadFile =File(...),db: Session = Depends(connection.get_db),  db1: Session =Depends(auth_user),):
    #comprueba si existe el archivo en files2
    existe= path.exists("files2")
    if existe:
        await delete_file("files2")
        mkdir("files2")
    else :
        mkdir("files2")
    with open(getcwd()+"/files2/"+ file.filename, "wb") as myfile:
        content = await file.read()
        myfile.write(content)
        myfile.close()
        lista=procesar_archivo.comprobar2(file.filename)
        busqueda=lista
    
        new_list = model.Listas(firstname = busqueda['FirstName']
                            , listofac = busqueda['ListOfac']
                            , listonu = busqueda['ListOnu']
                            , listfbi = busqueda['ListFbi']
                            , finddate = busqueda['FindDate']
                            , consulta = busqueda['Consulta']
                            , user = users
                            )
        db.add(new_list)
        db.commit()
        db.refresh(new_list) 
        sendmail.sendmail(email)
        return new_list

#POST
#Realiza busqueda por cargue de archivo cruzando todas las listas y envial  al correo
@app.post("/uploadMassive2/{coincidencia}",tags=["Upload"])
async def uploadfilemassive(coincidencia:int,file:UploadFile =File(...),db: Session = Depends(connection.get_db)):
    query = db.query(model.Listas_add)
    query = query.order_by(desc(model.Listas_add.fecha))
    lists = query.all()
    

    existe= path.exists("files2")
    if existe:
        await delete_file("files2")
        mkdir("files2")
    else :
        mkdir("files2")
    with open(getcwd()+"/files2/"+ file.filename, "wb") as myfile:
        content = await file.read()
        myfile.write(content)
        myfile.close()
        lista = procesar_archivo.comprobar3(file.filename,lists,coincidencia)
        busqueda = lista
    
        # new_list = model.Listas(firstname = busqueda['FirstName']
        #                     , listofac = busqueda['ListOfac']
        #                     , listonu = busqueda['ListOnu']
        #                     , listfbi = busqueda['ListFbi']
        #                     , finddate = busqueda['FindDate']
        #                     , consulta = busqueda['Consulta']
        #                     , user = users
        #                     )
        # db.add(new_list)
        # db.commit()
        # db.refresh(new_list) 
        # file_path = path.join(path.abspath(getcwd()), "", 'mi_dataframe.xlsx')
        # return FileResponse(file_path)


        # sendmail.sendmail(email)
        return lista

#POST
#Recibe parametros para presentar informe individual 
@app.post("/Informe/{nombre_busca}/{coincidencia}/{lists}")
async def info_person(nombre_busca:str, coincidencia:int,lists:str,db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    con.reportepdf(nombre_busca,coincidencia,lists)
    path=getcwd()+"/"+settings.NAME_ARCHIVO_REPORTE3
    return FileResponse(path, media_type="application/pdf", filename="tabla2.pdf")


#POST
#Recibe parametros para presentar informe individual 
@app.get("/listas", response_model=List[schema.List_addFound], tags=['Upload'])
async def info_listas( db: Session = Depends(connection.get_db), settings: Settings = Depends(get_settings)):
    query = db.query(model.Listas_add)
    # query = query.order_by(desc(model.Listas_add.fecha))
    lists = query.all()
    return lists 

# DELETE
#Elimina Usuarios
@app.delete("/listas/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int,  db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    listas = db.get(model.Listas_add, id)
    if listas:
        db.delete(listas)
        db.commit()


"""
GET METHOD
Se encarga de hacer consultas en la web medio de una api de busqueda de google

INPUT = search_query:str, language:str, number_of_articles:int
OUTPUT =  {
       "title": "",
       "link": "",
     }
"""
@app.get("/Google/{search_query}/{department}/{languaje}/{number_of_articles}")
async def search_engine(search_query:str, department:str, language:str = "lang_es", number_of_articles:int = 5, db:Session = Depends(auth_user)):
    
    __keys = { "key": "AIzaSyDTaSnGNLxM_O-IMkvupJvt9vOcDm4VAD4", "cx": "90138e4e270fb468d" }

    terms = find_words_key(department)
    # terms = ['theft', 'captacion', 'ilegal', 'kidnapping', 'lawsuit', 'fraud', 'missing']

    formatted_query = "(" + "|".join(terms) + ")" + f" {search_query}"
    
    url = "https://www.googleapis.com/customsearch/v1"
    data = {'key': __keys['key'], 'cx': __keys['cx'], 'q': formatted_query, 'lr': language, 'num': number_of_articles}

    response = requests.get(url, data)
    items = response.json()['items']
    filtered_items = [{"title": item["title"], "link": item["link"]} for item in items]
    
    if response.status_code == 200:
        return JSONResponse(content=filtered_items)
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="No se ha encontrado el sitio web")
    elif response.status_code == 500:
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    elif response.status_code == 403:
        raise HTTPException(status_code=403, detail="Forbidden")
        

def find_words_key(name:str):
    lists = procesar_archivo.words_keys(name)
    return lists


#POST
#Recibe parametros para crear categoria 
@app.post("/department/{department}")
async def info_person(department:str,db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    ok=procesar_archivo.create_department(department)
    return ok

#POST
#Recibe parametros para añadir palabra clave
@app.post("/department_word/{department}/{word}")
async def info_person(department:str,word:str,db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    ok=procesar_archivo.add_word_key(department,word)
    return ok

#GET
#Recibe department para traer lista
@app.get("/department_word/")
async def info_person(db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    ok=procesar_archivo.get_departments()
    return ok

#GET
#Recibe department para traer lista
@app.get("/department_word/{department}")
async def info_person(department:str,db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    ok=procesar_archivo.words_keys(department)
    return ok

#GET
#Recibe PATH PARA DESCARGAR 
@app.get("/download/{file_path:path}")
async def download_file(file_path: str, response: Response):
    file_path = file_path[1:]
    if os.path.isfile(file_path):
        with open(file_path, "rb") as file:
            contents = file.read()
        file_extension = os.path.splitext(file_path)[1]
        # print(file_extension) # Uncomment this line to check the file extension
        media_type = f"image/{file_extension[1:]}" # Update this line to set the media type dynamically based on the file extension
        response.headers["Content-Disposition"] = f"attachment; filename={file_path}"
        return Response(content=contents, media_type=media_type, status_code=200)
    else:
        return {"detail": "File not found."}
    

# Definir un endpoint en FastAPI que llama a la función get_lists para actualizar listas!
@app.get("/actualizar_registros",tags=['Upload'])
def  get_lists(db: Session = Depends(connection.get_db)):
    datos = requests.get(dato.URLACTUALIZA) 
    datos_dict = json.loads(datos.content)
    today = str(date.today())
    registros_ofac = datos_dict['registros_ofac']
    registros_onu = datos_dict['registros_onu']
    registros_fbi = datos_dict['registros_fbi']
    name_ofac = "LISTA OFAC"
    name_onu = "LISTA ONU"
    name_fbi = "LISTA FBI"

    ofac = db.query(model.Registros).filter(model.Registros.descripcion == name_ofac).first()
    ofac.registros = registros_ofac 
    ofac.fecha = today 
    db.commit()

    onu = db.query(model.Registros).filter(model.Registros.descripcion == name_onu).first()
    onu.registros = registros_onu 
    onu.fecha = today 
    db.commit()

    fbi = db.query(model.Registros).filter(model.Registros.descripcion == name_fbi).first()
    fbi.registros = registros_fbi 
    fbi.fecha = today 
    db.commit()

    return {"message": "Registros actualizados correctamente"}


# Definir un endpoint en FastAPI que llama a la función get_lists
@app.get("/mostrar_registros",tags=['Upload'])
def  get_registros(db: Session = Depends(connection.get_db)):
    registros = db.query(model.Registros)
    registros = registros.order_by(model.Registros.id)
    lists = registros.all()
    return lists

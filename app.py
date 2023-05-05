import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
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
from datetime import datetime, timedelta
from jose import jwt, JWTError
from os import getcwd, mkdir, path, rename
import shutil
import pandas as pd
from PIL import Image
import requests

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
    return busqueda

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
    return busqueda
    

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
    acess_token = {"sub":form.username,"rol":user_db.rol,  "exp": datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_DURATION)}

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

#GET
#Obtiene lista individual de personas añadidas
@app.get("/Userban")
async def get_person(db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    lista = listaperson.leerlistaperson()
    return lista

#POST
#Carga usuario individual 
@app.post("/Userban/{nombre}/{identificacion}/{tipo_identificacion}/{direccion}/{ciudad}/{pais}")
async def uploadfile(nombre:str, identificacion:str, tipo_identificacion:str, direccion:str,ciudad:str,pais:str,file:UploadFile =File(...),db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    link_photo = "/photos/"+ file.filename
    with open(getcwd()+"/photos/"+ file.filename, "wb") as myfile:
        content = await file.read()
        myfile.write(content)
        myfile.close()
    
    listaperson.add_person(nombre,identificacion,tipo_identificacion,direccion,ciudad,pais,link_photo)
    return True

#POST
#Carga usuario individual 
@app.post("/Userban/{nombre_busca}/{coincidencia}")
async def find_person(nombre_busca:str, coincidencia:int,db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    lista = listaperson.buscarlistaperson(nombre_busca,coincidencia)
    ruta_imagen = getcwd()+lista[0]['link_photo']
    imagen = Image.open(ruta_imagen)
    imagen.show()
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
async def findcharge(name:str, coincidencia:int , db1: Session =Depends(auth_user)):
    comprueba= procesar_archivo.buscar(name, coincidencia)
    return comprueba

#GET
#Descarga lista cargada
@app.get("/downloadcharge")
async def findcharge(name:str,  db1: Session =Depends(auth_user), settings: Settings = Depends(get_settings)):
    
    return FileResponse(getcwd()+"files/"+settings.NAME_ARCHIVO_CARGUE)

#POST
#Realiza busqueda por cargue de archivo cruzando todas las listas y envial  al correo
@app.post("/uploadMassive/{email}/{users}")
async def uploadfilemassive(email:str,users:str,file:UploadFile =File(...),db: Session = Depends(connection.get_db),  db1: Session =Depends(auth_user),):
    
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
#Recibe parametros para presentar informe individual 
@app.post("/Informe/{nombre_busca}/{coincidencia}/{listaofac}/{listaonu}/{listafbi}")
async def info_person(nombre_busca:str, coincidencia:int,listaofac:str,listaonu:str, listafbi:str,db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    con.reportepdf(nombre_busca,coincidencia,listaofac,listaonu,listafbi)
    
    return FileResponse(getcwd()+"/"+settings.NAME_ARCHIVO_REPORTE3)


#POST
#Recibe parametros para presentar informe individual 
@app.get("/listas")
async def info_person(nombre_busca:str,db1: Session =Depends(auth_user),settings: Settings = Depends(get_settings)):
    con.reportepdf(nombre_busca,coincidencia,listaofac,listaonu,listafbi)
    
    return FileResponse(getcwd()+"/"+settings.NAME_ARCHIVO_REPORTE3)


"""
GET METHOD
Se encarga de hacer consultas en la web medio de una api de busqueda de google

INPUT = search_query:str, language:str, number_of_articles:int
OUTPUT =  {
       "title": "",
       "link": "",
     }
"""
@app.get("/Google/")
async def search_engine(search_query:str, language:str = "lang_es", number_of_articles:int = 5):
    __keys = { "key": "AIzaSyBoKUC3NFQ36iYZj4_Y-wASaAInvr6XVcc", "cx": "e5a2b555bf5da4fda" }
    tems = ['robo', 'estafa', 'asesinato', 'secuestro', 'demanda']
    
    formatted_query = "(" + "|".join(tems) + ")" + f" {search_query}"
    
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
        


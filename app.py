from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from utils import connection,consume, procesar_archivo
from models import schema
from models import model
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext 
from datetime import datetime, timedelta
from jose import jwt, JWTError
from os import getcwd, mkdir, path
import shutil

ALGORITHM="HS256"
ACCESS_TOKEN_DURATION = 5
SECRET = "761c78b692385bd23194ea3848b266589f4c4f16e245b0c7a977c29741bee075"

tokensito=''

app = FastAPI()

crypt = CryptContext(schemes=["bcrypt"])

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
    
    # if token == tokensito:
    #     return True
    # else:
    #     return False
    

#Busca el usuario en la base de datos
def search_user_db(username:str, lists: list):
    for email in lists:    
        if username == email.email:
            return email
    return False

#Busca la contraseña del usuario
def search_password_db(lists:list,pos:str, passw:str):
    
    for password in lists:   
        if password.id == pos: 
            if password.password ==passw:
                return passw

#GET
#consulta en las listas y devuelve lista
@app.get("/Consume/{nombre_busca}")
async def Consume(nombre_busca:str,db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    busqueda=consume.consumir(nombre_busca)
    
    new_list = model.Listas(firstname = busqueda['FirstName']
                            , listofac = busqueda['ListOfac']
                            , listonu = busqueda['ListOnu']
                            , listfbi = busqueda['ListFbi']
                            , finddate = busqueda['FindDate']
                            , consulta = busqueda['Consulta']
                            )
    db.add(new_list)
    db.commit()
    db.refresh(new_list) 
    return new_list

#GET
#Obtiene todos los usuarios
@app.get("/Busquedas", response_model=List[schema.PersonFound])
async def GetAll1(db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    query = db.query(model.Listas)
    lists = query.all()
    return lists

#GET
#Obtiene todos los usuarios
@app.get("/User", response_model=List[schema.UserFound])
async def GetAll(db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    query = db.query(model.User)
    lists = query.all()
    return lists


# POST
#Crea usuarios
@app.post("/User", response_model=schema.UserFound)
async def Post(userFound: schema.UserFoundCreate, db: Session = Depends(connection.get_db), db1: Session =Depends(auth_user)):
    new_list2 = model.User(  firstname = userFound.firstname
                            ,password = userFound.password
                            ,email= userFound.email
                            ,createdate = userFound.createdate
                            )
    # add it to the session and commit it
    db.add(new_list2)
    db.commit()
    
    # update the patient instance to get the newly created Id
    db.refresh(new_list2) 
    # retorna lista
    return new_list2

# PUT
#Edita a los usuarios
@app.put("/User/{ID}", response_model=schema.UserFound)
async def Put(ID: int, listsUpdate:schema.UserFound, db: Session = Depends(connection.get_db)):
    
    lists = db.get(model.User, ID) 
    if lists:
        lists.firstname = listsUpdate.firstname
        lists.password = listsUpdate.password
        lists.email = listsUpdate.email
        db.commit()
        db.refresh(lists)

    if not lists:
        raise HTTPException(status_code=404, detail=f"lists with ID {ID} not found")

    return lists

#POST
#logea al usuario
@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(connection.get_db)):
    prueba = await GetAll(db)    

    user_db = search_user_db(form.username,prueba)
    
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

    
    if not crypt.verify(form.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")

    if user_db is True:
        user_db=form.username
    acess_token = {"sub":form.username,  "exp": datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_DURATION)}

    return {"access_token": jwt.encode(acess_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@app.post("/upload")
async def uploadfile(file:UploadFile =File(...)):
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
        procesar_archivo.comprobar(file.filename)
    return "success"

@app.delete("/delete")
async def delete_file(folder_name:str):
        shutil.rmtree(getcwd() +"/" + folder_name)
        return JSONResponse(content={
            "removed": True,}
            ,status_code=200)

@app.get("/findcharge/{name}")
async def findcharge(name:str):
    comprueba= procesar_archivo.buscar(name)
    return comprueba
from . import jwt_auth_users
from fastapi import FastAPI
from routers import individual,listas

app = FastAPI()

app.include_router(individual.router)
app.include_router(listas.router)
app.include_router(jwt_auth_users.router)
# app.include_router(basic_auth_users.router)

# app.mount("/static",StaticFiles(directory="static"),name="static")



#Routers

@app.get("/")
async def root():
    return {"message": "Hello World"}
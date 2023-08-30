# Api-Backend-Listas

#Descargar Python: Ve a la página oficial de descargas de Python y descarga la versión que necesites.

#Instalar Python: Ejecuta el archivo descargado y sigue las instrucciones. Asegúrate de marcar la casilla "Add Python to PATH" durante la instalación.

#Verificar la Instalación: Abre una nueva ventana de terminal (CMD) y ejecuta:

python --version

Instalar FastAPI y Hypercorn: Instala FastAPI y Hypercorn usando pip:
pip install fastapi hypercorn

#Correr FastAPI con Hypercorn: Navega a la carpeta de tu proyecto y ejecuta el siguiente comando (reemplaza main:app con la ubicación de tu aplicación FastAPI):

hypercorn main:app --bind 0.0.0.0:8080

#para configurar de acuerdo a tu base de datos debes dirigirte a la siguiente ruta: utils/connection en la linea 15 te aparecera:

 engine = create_engine(f'postgresql://{settings.DB_UID}:{settings.DB_PWD}@{settings.DB_SERVER}:{settings.DB_PORT}/{settings.DB_NAME}')
#En estos momentos lo tengo con unas variables de entorno si deseas hacerlo manual seria remplazando el contenido de las llaves
#
#esta es de postgress si quieres de SQL 

engine = create_engine(f'mssql+pyodbc://{settings.DB_UID}:{settings.DB_PWD}@{settings.DB_SERVER}:{settings.DB_PORT}/{settings.DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server')

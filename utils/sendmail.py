import smtplib
from fastapi import Depends
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from .config import get_settings

def sendmail(email:str):
    dato=get_settings()    
    remitente = dato.EMAIL
    destinatarios = email
    asunto = '[RPI] Correo de prueba'
    cuerpo = 'Hola estimado este es el resultado de la busqueda masiva'

    # Creamos el objeto mensaje
    mensaje = MIMEMultipart()
    # Establecemos los atributos del mensaje
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = asunto

    # Agregamos el cuerpo del mensaje como objeto MIME de tipo texto
    mensaje.attach(MIMEText(cuerpo, 'plain'))
    # Abrimos el archivo que vamos a adjuntar
    archivo_adjunto = open(dato.NAME_ARCHIVO_REPORTE2, 'rb')
    # Creamos un objeto MIME base
    adjunto_mime = MIMEBase('application', 'octet-stream')
    # Y le cargamos el archivo adjunto
    adjunto_mime.set_payload((archivo_adjunto).read())
    # Codificamos el objeto en BASE64
    encoders.encode_base64(adjunto_mime)
    # Agregamos una cabecera al objeto
    adjunto_mime.add_header('Content-Disposition', "attachment; filename= %s" % dato.NAME_ARCHIVO_REPORTE2)
    # Y finalmente lo agregamos al mensaje
    mensaje.attach(adjunto_mime)
    # Creamos la conexión con el servidor
    sesion_smtp = smtplib.SMTP('smtp.gmail.com', 587) 
    # Ciframos la conexión
    sesion_smtp.starttls()
    
    # Iniciamos sesión en el servidor
    sesion_smtp.login(dato.EMAIL,dato.CONTRASEÑA_EMAIL)

    # Convertimos el objeto mensaje a texto
    texto = mensaje.as_string()

    # Enviamos el mensaje
    sesion_smtp.sendmail(remitente, destinatarios, texto)

    # Cerramos la conexión
    sesion_smtp.quit()
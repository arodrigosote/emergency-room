
from datetime import datetime
import os

def log_message(message):
    # Obtener la fecha y hora actual
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    # Mensaje a escribir en el archivo
    log_entry = f"{timestamp} - {message}\n"
    # Escribir el mensaje en el archivo 'server_log.txt' dentro de la carpeta 'history'
    with open('history/server_log.txt', 'a') as log_file:
        log_file.write(log_entry)

def log_database(message):
    # Obtener la fecha y hora actual
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    # Mensaje a escribir en el archivo
    log_entry = f"{timestamp} - {message}\n"
    # Escribir el mensaje en el archivo 'db_log.txt' dentro de la carpeta 'history'
    with open('history/db_changes.txt', 'a') as log_file:
        log_file.write(log_entry)
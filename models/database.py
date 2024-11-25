import sqlite3
from utils.log import log_message
import os
from datetime import datetime

def execute_query(query: str) -> bool:
    try:
        # Asumiendo que la conexión a la base de datos es a través de sqlite3
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        log_message(f"Query ejecutada con éxito: {query}")
        return True
    except Exception as e:
        log_message(f"Error ejecutando query: {e}")
        return False

def obtener_cambios_db():
    """
    Lee las consultas del archivo 'db_changes.txt', extrae la fecha y la consulta,
    y las ordena del más antiguo al más nuevo.

    Retorna:
        str: Una cadena con las consultas ordenadas por fecha, separadas por saltos de línea.
    """
    archivo_path = os.path.join("history", "db_changes.txt")

    try:
        if not os.path.exists(archivo_path):
            log_message("[Error] El archivo 'db_changes.txt' no existe.")
            return ""

        consultas = []
        with open(archivo_path, "r") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue  # Ignorar líneas vacías
                # Dividir por el separador esperado " - # "
                partes = linea.split(" - # ", 1)
                if len(partes) == 2:
                    fecha, consulta = partes[0], partes[1]
                    consultas.append((fecha, consulta))
                else:
                    log_message(f"[Error] Formato incorrecto en la línea: {linea}")

        # Ordenar por fecha (se asume que las fechas están en formato ISO 8601, como "YYYY-MM-DD HH:MM:SS")
        consultas.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S"))

        # Convertir las consultas a una cadena separada por saltos de línea
        consultas_ordenadas = "\n".join([f"{fecha} - # {consulta}" for fecha, consulta in consultas])
        return consultas_ordenadas

    except Exception as e:
        log_message(f"[Error] No se pudo leer o procesar 'db_changes.txt': {e}")
        return ""


def guardar_cambios_db_changestomake(queries):
    """
    Guarda las consultas en el archivo 'changestomake.txt' dentro de la carpeta 'database'.
    Si el archivo no existe, lo crea.

    Args:
        queries (str): Las consultas a guardar.
    """
    archivo_path = os.path.join("database", "changestomake.txt")

    try:
        # Crear la carpeta 'database' si no existe
        os.makedirs(os.path.dirname(archivo_path), exist_ok=True)

        # Abrir el archivo en modo append para no borrar el contenido anterior
        with open(archivo_path, "a") as archivo:
            archivo.write(queries + "\n")
        
        log_message(f"Consultas guardadas en 'changestomake.txt': {queries}")
    except Exception as e:
        log_message(f"[Error] No se pudo guardar en 'changestomake.txt': {e}")

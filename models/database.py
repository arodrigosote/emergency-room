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
        str: Una cadena con las consultas ordenadas por fecha.
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
                try:
                    # Dividir por el separador esperado " - # "
                    partes = linea.split(" - # ", 1)
                    if len(partes) != 2:
                        log_message(f"[Error] Formato incorrecto en la línea: {linea}")
                        continue

                    fecha, consulta = partes[0], partes[1]
                    consultas.append((fecha, consulta))
                except Exception as e:
                    log_message(f"[Error] No se pudo procesar la línea: {linea}. Detalle: {e}")
                    continue

        # Ordenar por fecha (se asume que las fechas están en formato ISO 8601, como "YYYY-MM-DD HH:MM:SS")
        consultas.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S"))

        # Convertir a una cadena para enviar
        consultas_ordenadas = "\n".join([f"{fecha} - # {consulta}" for fecha, consulta in consultas])
        return consultas_ordenadas

    except Exception as e:
        log_message(f"[Error] No se pudo leer o procesar 'db_changes.txt': {e}")
        return ""

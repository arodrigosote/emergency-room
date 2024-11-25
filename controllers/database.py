from utils.log import log_message
import sqlite3
import os
from datetime import datetime


def init_db():
    # Inicializa la base de datos
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    
    # Leer el archivo SQL desde la carpeta database en la raíz del proyecto
    script_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
    with open(script_path, 'r') as f:
        sql_script = f.read()
    
    # Ejecutar el script SQL
    cursor.executescript(sql_script)
    
    conn.commit()
    conn.close()
    log_message("[Base de Datos] Base de datos inicializada.")




def agregar_salas_emergencia():
    salas = [
        ('Sala 0', '192.168.174.138', 5),
        ('Sala 1', '192.168.174.139', 5),
        ('Sala 2', '192.168.174.140', 5),
        ('Sala 3', '192.168.174.141', 5),
        ('Sala 4', '192.168.174.142', 5)
    ]
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            INSERT INTO salas_emergencia (nombre, ip, capacidad_total, capacidad_disponible) VALUES (?, ?, ?, ?)
        """
        
        for sala in salas:
            cursor.execute(query, (sala[0], sala[1], sala[2], sala[2]))
        
        conn.commit()
        log_message("[Base de Datos] 3 salas de emergencia agregadas a la base de datos.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo agregar las salas de emergencia: {e}")
    finally:
        conn.close()
"""
    # Manejo del historial
    history_dir = os.path.join(os.path.dirname(__file__), '..', 'history')
    os.makedirs(history_dir, exist_ok=True)
    history_file = os.path.join(history_dir, 'db_changes.txt')

    # Escribir las líneas en el archivo
    with open(history_file, 'a') as f:
        for sala in salas:
            formatted_query = f"INSERT INTO salas_emergencia (nombre, capacidad_total, capacidad_disponible) VALUES ('{sala[0]}', {sala[1]}, {sala[1]})"
            f.write(f"# Agregada sala de emergencia: {sala[0]}, Capacidad Total: {sala[1]}\n")
            f.write(f"& {formatted_query}\n")
"""




def mostrar_log_servidor():
    log_path = os.path.join(os.path.dirname(__file__), '..', 'history', 'server_log.txt')
    try:
        with open(log_path, 'r') as f:
            log_content = f.read()
        print(log_content)
    except FileNotFoundError:
        print("[Error] No se encontró el archivo de log del servidor.")

def mostrar_log_base_datos():
    log_path = os.path.join(os.path.dirname(__file__), '..', 'history', 'db_changes.txt')
    try:
        with open(log_path, 'r') as f:
            log_content = f.read()
        print(log_content)
    except FileNotFoundError:
        print("[Error] No se encontró el archivo de log de la base de datos.")

def mostrar_log_changestomake():
    log_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'changestomake.txt')
    try:
        with open(log_path, 'r') as f:
            log_content = f.read()
        print(log_content)
    except FileNotFoundError:
        print("[Error] No se encontró el archivo de log de la base de datos.")







##
##  No se guarda en changestomake ningun cambio para ser enviado.
##

def ejecutar_dbchanges():
    archivo_path = os.path.join("database", "changestomake.txt")
    
    # Verificar si el archivo existe
    if not os.path.exists(archivo_path):
        log_message("El archivo changestomake.txt no existe.")
        return
    
    # Leer las líneas del archivo
    with open(archivo_path, "r") as archivo:
        lineas = archivo.readlines()
    
    # Parsear las líneas en una lista de tuplas (fecha_hora, consulta)
    registros = []
    for linea in lineas:
        linea = linea.strip()
        if linea:
            try:
                fecha_hora, consulta = linea.split("- #", 1)
                registros.append((datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S"), consulta))
                
            except ValueError:
                log_message(f"Línea ignorada por formato incorrecto: {linea}")
    
    # Ordenar los registros por fecha y hora
    registros_ordenados = sorted(registros, key=lambda x: x[0])
    log_message(f"Registros ordenados: {registros_ordenados}")
    # Ejecutar las consultas en orden
    for fecha_hora, consulta in registros_ordenados:
        try:
            execute_query(consulta)  # Llamar a la función que ejecuta la consulta
            log_message(f"Consulta ejecutada: {consulta}")
        except Exception as e:
            log_message(f"Error ejecutando consulta: {consulta}. Detalles: {e}")


def execute_query(consulta):
    # Conexión a la base de datos
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    
    # Ejecutar la consulta
    cursor.execute(consulta)
    conn.commit()
    
    # Cerrar la conexión
    conn.close()
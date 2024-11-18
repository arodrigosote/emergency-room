import sqlite3
import os

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
    print("[Base de Datos] Base de datos inicializada.")

def agregar_sala_emergencia(nombre, capacidad_total):
    # Agrega una nueva sala de emergencia en la base de datos
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO salas_emergencia (nombre, capacidad_total, capacidad_disponible)
        VALUES (?, ?, ?)
    ''', (nombre, capacidad_total, capacidad_total))
    conn.commit()
    conn.close()
    print(f"[Base de Datos] Sala de emergencia '{nombre}' agregada con capacidad total de {capacidad_total}.")
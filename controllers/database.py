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
    print("\n[Base de Datos] Base de datos inicializada.")

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
    print(f"\n[Base de Datos] Sala de emergencia '{nombre}' agregada con capacidad total de {capacidad_total}.")

def listar_salas_emergencia():
    # Lista todas las salas de emergencia en la base de datos y las muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM salas_emergencia')
    salas = cursor.fetchall()
    conn.close()

    # Mostrar las salas en una tabla por consola sin utilizar tabulate
    headers = ["ID Sala", "Nombre", "Estado", "Es Maestro", "Capacidad Total", "Capacidad Disponible"]
    print(f"{headers[0]:<10} {headers[1]:<20} {headers[2]:<10} {headers[3]:<10} {headers[4]:<15} {headers[5]:<20}")
    print("-" * 85)
    for sala in salas:
        print(f"{sala[0]:<10} {sala[1]:<20} {sala[2]:<10} {sala[3]:<10} {sala[4]:<15} {sala[5]:<20}")
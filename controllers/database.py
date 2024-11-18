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


def agregar_doctores():
    doctores = [
        ('Dr. Juan Pérez', 'Cardiología'),
        ('Dra. Ana Gómez', 'Neurología'),
        ('Dr. Luis Martínez', 'Pediatría'),
        ('Dra. María Rodríguez', 'Dermatología'),
        ('Dr. Carlos Sánchez', 'Gastroenterología')
    ]
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            INSERT INTO doctores (nombre, especialidad) VALUES (?, ?)
        """
        
        cursor.executemany(query, doctores)
        conn.commit()
        print("\n[Base de Datos] 5 doctores agregados a la base de datos.")
    except sqlite3.Error as e:
        print(f"\n[Error] No se pudo agregar los doctores: {e}")
    finally:
        conn.close()

    # Manejo del historial
    history_dir = os.path.join(os.path.dirname(__file__), '..', 'history')
    os.makedirs(history_dir, exist_ok=True)
    history_file = os.path.join(history_dir, 'db_changes.txt')

    # Escribir las líneas en el archivo
    with open(history_file, 'a') as f:
        for doctor in doctores:
            formatted_query = f"INSERT INTO doctores (nombre, especialidad) VALUES ('{doctor[0]}', '{doctor[1]}')"
            f.write(f"# Agregado doctor: {doctor[0]}, Especialidad: {doctor[1]}\n")
            f.write(f"& {formatted_query}\n")


def agregar_salas_emergencia():
    salas = [
        ('Sala 0', 10),
        ('Sala 1', 15),
        ('Sala 2', 20)
    ]
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            INSERT INTO salas_emergencia (nombre, capacidad_total, capacidad_disponible) VALUES (?, ?, ?)
        """
        
        for sala in salas:
            cursor.execute(query, (sala[0], sala[1], sala[1]))
        
        conn.commit()
        print("\n[Base de Datos] 3 salas de emergencia agregadas a la base de datos.")
    except sqlite3.Error as e:
        print(f"\n[Error] No se pudo agregar las salas de emergencia: {e}")
    finally:
        conn.close()

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


import sqlite3
import os
from utils.log import log_message, log_database
from models.node import procesar_consulta

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
        log_message("[Base de Datos] 5 doctores agregados a la base de datos.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo agregar los doctores: {e}")
    finally:
        conn.close()

def agregar_doctor():
    nombre = input("Ingrese el nombre del doctor: ")
    especialidad = input("Ingrese la especialidad del doctor: ")
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            INSERT INTO doctores (nombre, especialidad) VALUES (?, ?)
        """
        
        cursor.execute(query, (nombre, especialidad))
        conn.commit()
        mensaje = f"INSERT INTO doctores (nombre, especialidad) VALUES ('{nombre}', '{especialidad}')"
        log_database(f"# INSERT INTO doctores (nombre, especialidad) VALUES ('{nombre}', '{especialidad}')")
        procesar_consulta(mensaje)
        log_message(f"[Base de Datos] Doctor {nombre} agregado a la base de datos.")
        print(f"Doctor {nombre} agregado a la base de datos.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo agregar el doctor: {e}")
        print(f"Error al agregar el doctor: {e}")
    finally:
        conn.close()

def actualizar_doctor():
    listar_doctores()
    id_doctor = input("Ingrese el ID del doctor a actualizar: ")
    
    # Validar si el ID existe en la base de datos
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM doctores WHERE id_doctor = ?', (id_doctor,))
        if cursor.fetchone()[0] == 0:
            log_message(f"[Error] El ID {id_doctor} no existe en la base de datos.")
            print(f"El ID {id_doctor} no existe en la base de datos.")
            conn.close()
            return
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo validar el ID del doctor: {e}")
        print(f"Error al validar el ID del doctor: {e}")
        conn.close()
        return
    
    nuevo_nombre = input("Ingrese el nuevo nombre del doctor: ")
    nueva_especialidad = input("Ingrese la nueva especialidad del doctor: ")
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            UPDATE doctores
            SET nombre = ?, especialidad = ?
            WHERE id_doctor = ?
        """
        
        cursor.execute(query, (nuevo_nombre, nueva_especialidad, id_doctor))
        conn.commit()
        mensaje = f"UPDATE doctores SET nombre = '{nuevo_nombre}', especialidad = '{nueva_especialidad}' WHERE id_doctor = {id_doctor}"
        log_database(f"# UPDATE doctores SET nombre = '{nuevo_nombre}', especialidad = '{nueva_especialidad}' WHERE id_doctor = {id_doctor}")
        procesar_consulta(mensaje)
        log_message(f"[Base de Datos] Doctor {nuevo_nombre} actualizado en la base de datos.")
        print(f"Doctor {nuevo_nombre} actualizado en la base de datos.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo actualizar el doctor: {e}")
        print(f"Error al actualizar el doctor: {e}")
    finally:
        conn.close()

def listar_doctores():
    # Lista todos los doctores en la base de datos y los muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM doctores')
    doctores = cursor.fetchall()
    conn.close()

    # Mostrar los doctores en una tabla por consola sin utilizar tabulate
    headers = ["ID Doctor", "Nombre", "Especialidad", "Turno"]
    print(f"{headers[0]:<10} {headers[1]:<20} {headers[2]:<20} {headers[3]:<10}")
    print("-" * 65)
    for doctor in doctores:
        print(f"{doctor[0]:<10} {doctor[1]:<20} {doctor[2]:<20} {doctor[3]:<10}")

def listar_doctores_ocupados():
    # Lista todos los trabajadores sociales en la base de datos y los muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM doctores WHERE estado = "ocupado"')
    doctores = cursor.fetchall()
    conn.close()

    # Mostrar los trabajadores sociales en una tabla por consola sin utilizar tabulate
    headers = ["ID Doctor", "Nombre"]
    print(f"{headers[0]:<15} {headers[1]:<20}")
    print("-" * 35)
    for doctor in doctores:
        print(f"{doctor[0]:<15} {doctor[1]:<20}")
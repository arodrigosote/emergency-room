import sqlite3
import os
from utils.log import log_message

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
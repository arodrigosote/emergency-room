import sqlite3
import os
from utils.log import log_message, log_database
from models.node import procesar_consulta

def agregar_trabajadores_sociales():
    trabajadores = [
        ('Trabajador 1'),
        ('Trabajador 2'),
        ('Trabajador 3'),
        ('Trabajador 4'),
        ('Trabajador 5')
    ]
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            INSERT INTO trabajadores_sociales (nombre) VALUES (?)
        """
        
        cursor.executemany(query, [(trabajador,) for trabajador in trabajadores])
        conn.commit()
        log_message("[Base de Datos] 5 trabajadores sociales agregados a la base de datos.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo agregar los trabajadores sociales: {e}")
    finally:
        conn.close()

    
def agregar_trabajador():
    nombre = input("Ingrese el nombre del trabajador: ")
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            INSERT INTO trabajadores_sociales (nombre) VALUES (?)
        """
        
        cursor.execute(query, (nombre))
        conn.commit()
        mensaje = f"INSERT INTO trabajadores_sociales (nombre) VALUES ('{nombre}')"
        log_database(f"# INSERT INTO trabajadores_sociales (nombre) VALUES ('{nombre}')")
        procesar_consulta(mensaje)
        log_message("[Base de Datos] Trabajador agregado a la base de datos.")
        print(f"Trabajador: {nombre} agregado a la base de datos.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo agregar el doctor: {e}")
        print(f"Error al agregar el trabajador: {e}")
    finally:
        conn.close()

def listar_trabajadores_sociales():
    # Lista todos los trabajadores sociales en la base de datos y los muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trabajadores_sociales')
    trabajadores = cursor.fetchall()
    conn.close()

    # Mostrar los trabajadores sociales en una tabla por consola sin utilizar tabulate
    headers = ["ID Trabajador", "Nombre"]
    print(f"{headers[0]:<15} {headers[1]:<20}")
    print("-" * 35)
    for trabajador in trabajadores:
        print(f"{trabajador[0]:<15} {trabajador[1]:<20}")

def actualizar_trabajador():
    listar_trabajadores_sociales()
    id_trabajador = input("Ingrese el ID del trabajador a actualizar: ")
    
    # Validar si el ID existe en la base de datos
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM trabajadores_sociales WHERE id = ?', (id_trabajador,))
        if cursor.fetchone()[0] == 0:
            log_message(f"[Error] El ID {id_trabajador} no existe en la base de datos.")
            print(f"El ID {id_trabajador} no existe en la base de datos.")
            conn.close()
            return
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo validar el ID del trabajador: {e}")
        print(f"Error al validar el ID del trabajador: {e}")
        conn.close()
        return
    
    nuevo_nombre = input("Ingrese el nuevo nombre del trabajador: ")
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            UPDATE trabajadores_sociales
            SET nombre = ?
            WHERE id = ?
        """
        
        cursor.execute(query, (nuevo_nombre, id_trabajador))
        conn.commit()
        mensaje = f"UPDATE trabajadores_sociales SET nombre = '{nuevo_nombre}' WHERE id = {id_trabajador}"
        log_database(f"# {mensaje}")
        procesar_consulta(mensaje)
        log_message(f"[Base de Datos] Trabajador {nuevo_nombre} actualizado en la base de datos.")
        print(f"Trabajador {nuevo_nombre} actualizado en la base de datos.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo actualizar el trabajador: {e}")
        print(f"Error al actualizar el trabajador: {e}")
    finally:
        conn.close()
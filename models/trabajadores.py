import sqlite3
import os
from utils.log import log_message

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
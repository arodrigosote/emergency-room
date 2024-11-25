import sqlite3
from utils.log import log_message

def agregar_camas():
    camas = [
        (1, 1, 'disponible'),
        (1, 2, 'disponible'),
        (1, 3, 'disponible'),
        (1, 4, 'disponible'),
        (1, 5, 'disponible'),
        (2, 1, 'disponible'),
        (2, 2, 'disponible'),
        (2, 3, 'disponible'),
        (2, 4, 'disponible'),
        (2, 5, 'disponible'),
        (3, 1, 'disponible'),
        (3, 2, 'disponible'),
        (3, 3, 'disponible'),
        (3, 4, 'disponible'),
        (3, 5, 'disponible'),
        (4, 1, 'disponible'),
        (4, 2, 'disponible'),
        (4, 3, 'disponible'),
        (4, 4, 'disponible'),
        (4, 5, 'disponible'),
        (5, 1, 'disponible'),
        (5, 2, 'disponible'),
        (5, 3, 'disponible'),
        (5, 4, 'disponible'),
        (5, 5, 'disponible')
    ]
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            INSERT INTO camas (id_sala, numero_cama, estado) VALUES (?, ?, ?)
        """
        
        cursor.executemany(query, camas)
        conn.commit()
        log_message("[Base de Datos] 15 camas agregadas a la base de datos.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo agregar las camas: {e}")
    finally:
        conn.close()

def listar_camas():
    # Lista todas las camas en la base de datos y las muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM camas')
    camas = cursor.fetchall()
    conn.close()

    # Mostrar las camas en una tabla por consola sin utilizar tabulate
    headers = ["ID Cama", "ID Sala", "Número", "Estado"]
    print(f"{headers[0]:<10} {headers[1]:<10} {headers[2]:<10} {headers[3]:<15}")
    print("-" * 45)
    for cama in camas:
        print(f"{cama[0]:<10} {cama[1]:<10} {cama[2]:<10} {cama[3]:<15}")


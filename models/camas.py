import sqlite3
from utils.log import log_message

def agregar_camas():
    camas = [
        (0, 1, 'Disponible'),
        (0, 2, 'Disponible'),
        (0, 3, 'Disponible'),
        (0, 4, 'Disponible'),
        (0, 5, 'Disponible'),
        (1, 1, 'Disponible'),
        (1, 2, 'Disponible'),
        (1, 3, 'Disponible'),
        (1, 4, 'Disponible'),
        (1, 5, 'Disponible'),
        (2, 1, 'Disponible'),
        (2, 2, 'Disponible'),
        (2, 3, 'Disponible'),
        (2, 4, 'Disponible'),
        (2, 5, 'Disponible')
    ]
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            INSERT INTO camas (sala_id, numero, estado) VALUES (?, ?, ?)
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


import sqlite3
import os


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


def agregar_sala_emergencia(nombre, capacidad_total):
    # Agrega una nueva sala de emergencia en la base de datos
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()

        # Usar parámetros para prevenir inyección SQL
        query = """
            INSERT INTO salas_emergencia (nombre, capacidad_total, capacidad_disponible) VALUES (?, ?, ?)
        """
        cursor.execute(query, (nombre, capacidad_total, capacidad_total))
        conn.commit()
        print(f"\n[Base de Datos] Sala de emergencia '{nombre}' agregada con capacidad total de {capacidad_total}.")
    except sqlite3.Error as e:
        print(f"\n[Error] No se pudo agregar la sala de emergencia: {e}")
    finally:
        conn.close()

    # Manejo del historial
    history_dir = os.path.join(os.path.dirname(__file__), '..', 'history')
    os.makedirs(history_dir, exist_ok=True)
    history_file = os.path.join(history_dir, 'db_changes.txt')

    # Escribir las dos líneas en el archivo
    with open(history_file, 'a') as f:
        formatted_query = f"INSERT INTO salas_emergencia (nombre, capacidad_total, capacidad_disponible) VALUES ('{nombre}', {capacidad_total}, {capacidad_total})"
        f.write(f"# Agregada sala de emergencia: {nombre}, Capacidad Total: {capacidad_total}\n")
        f.write(f"& {formatted_query}\n")
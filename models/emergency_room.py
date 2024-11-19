import sqlite3
import os
from utils.log import log_message, log_database
from models.node import enviar_mensaje_a_todos, enviar_mensaje_a_maestro
# from controllers.server_client import elegir_nodo_maestro  # Mover esta importación dentro de la función

def listar_salas_emergencia():
    # Lista todas las salas de emergencia en la base de datos y las muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM salas_emergencia')
    salas = cursor.fetchall()
    conn.close()

    # Mostrar las salas en una tabla por consola sin utilizar tabulate
    headers = ["ID Sala", "Nombre", "IP", "Estado", "Es Maestro", "Capacidad Total", "Capacidad Disponible"]
    header_line = "{:<10} {:<20} {:<15} {:<10} {:<15} {:<20} {:<20}".format(*headers)
    print(header_line)
    print("-" * len(header_line))
    for sala in salas:
        print(f"{sala[0]:<10} {sala[1]:<20} {sala[2]:<15} {sala[3]:<10} {sala[4]:<15} {sala[5]:<20} {sala[6]:<20}")


def agregar_sala_emergencia(nombre, capacidad_total, ip):
    # Agrega una nueva sala de emergencia en la base de datos
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()

        # Usar parámetros para prevenir inyección SQL
        query = """
            INSERT INTO salas_emergencia (nombre, ip, capacidad_total, capacidad_disponible) VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (nombre, ip, capacidad_total, capacidad_total))
        conn.commit()
        print(f"\n[Base de Datos] Sala de emergencia '{nombre}' agregada con capacidad total de {capacidad_total} y IP {ip}.")
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
        formatted_query = f"INSERT INTO salas_emergencia (nombre, capacidad_total, capacidad_disponible, ip) VALUES ('{nombre}', {capacidad_total}, {capacidad_total}, '{ip}')"
        f.write(f"# Agregada sala de emergencia: {nombre}, Capacidad Total: {capacidad_total}, IP: {ip}\n")
        f.write(f"& {formatted_query}\n")

def activar_sala(ip, nodo_maestro):
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        query = "UPDATE salas_emergencia SET estado = 'activado' WHERE ip = ?"
        cursor.execute(query, (ip,))
        conn.commit()
        log_database(f"UPDATE salas_emergencia SET estado = 'activado' WHERE ip = {ip}")
        log_message(f"[Sala] Estado de la sala con IP {ip} cambiado a activado.")
        
        # Obtener el nodo propio
        cursor.execute("SELECT * FROM salas_emergencia WHERE ip = ?", (ip,))
        nodo_propio = cursor.fetchone()
        if nodo_propio:
            log_message(f"[Nodo Propio] Nodo propio encontrado: {nodo_propio}")
            # Comparar con el nodo maestro
            if nodo_propio[2] == nodo_maestro['ip']:
                log_message("[Nodo] El nodo propio es el nodo maestro.")
                # Enviar mensaje a todos los nodos
                codigo = "10"
                mensaje = f"UPDATE salas_emergencia SET estado = 'activado' WHERE ip = '{ip}'"
                enviar_mensaje_a_todos(codigo, mensaje)
            else:
                log_message("[Nodo] El nodo propio no es el nodo maestro.")
                codigo = "11"
                mensaje = f"UPDATE salas_emergencia SET estado = 'activado' WHERE ip = '{ip}'"
                enviar_mensaje_a_maestro(nodo_maestro[2], codigo, mensaje)
        else:
            log_message("\n[Nodo Propio] No se encontró el nodo propio.")
    except sqlite3.Error as e:
        log_message(f"\n[Error] No se pudo activar la sala de emergencia: {e}")
    finally:
        conn.close()
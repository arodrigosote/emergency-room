import sqlite3
import os
from utils.log import log_message, log_database
from models.node import procesar_consulta
from datetime import datetime
from tabulate import tabulate

DB_PATH = 'nodos.db'


# Función auxiliar para conexión a la base de datos
def get_db_connection():
    return sqlite3.connect(DB_PATH)


def listar_salas_emergencia():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM salas_emergencia')
            salas = cursor.fetchall()

        # Mostrar las salas en formato de tabla
        headers = ["ID Sala", "Nombre", "IP", "Estado", "Es Maestro", "Capacidad Total", "Capacidad Disponible"]
        print(tabulate(salas, headers=headers, tablefmt="grid"))
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo listar las salas de emergencia: {e}")


def activar_sala(ip):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "UPDATE salas_emergencia SET estado = 'activado' WHERE ip = ?"
            cursor.execute(query, (ip,))
            conn.commit()
            
            log_database(f"# UPDATE salas_emergencia SET estado = 'activado' WHERE ip = '{ip}'")
            log_message(f"[Consulta] Activación de sala de emergencia con IP '{ip}' guardada en la base de datos.")

            cursor.execute("SELECT * FROM salas_emergencia WHERE ip = ?", (ip,))
            nodo_propio = cursor.fetchone()

            mensaje = f"UPDATE salas_emergencia SET estado = 'activado' WHERE ip = '{ip}'"

            procesar_consulta(mensaje)
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo activar la sala: {e}")


def obtener_sala_y_cama():
    try:
        with sqlite3.connect('nodos.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT salas_emergencia.id_sala 
                FROM salas_emergencia
                LEFT JOIN camas ON salas_emergencia.id_sala = camas.id_sala
                WHERE salas_emergencia.estado = 'activado' AND camas.estado = 'disponible'
                GROUP BY salas_emergencia.id_sala
                ORDER BY (CAST(COUNT(camas.id_cama) AS FLOAT) / salas_emergencia.capacidad_total) DESC
                LIMIT 1;
            """)
            sala = cursor.fetchone()

            if sala:
                cursor.execute("""
                    SELECT id_cama 
                    FROM camas 
                    WHERE id_sala = ? AND estado = 'disponible' 
                    LIMIT 1
                """, (sala[0],))
                cama = cursor.fetchone()

                if cama:
                    print(f"Cama disponible: {cama[0]}")
                    return sala[0], cama[0]
                else:
                    print("No hay camas disponibles en esta sala.")
                    return sala[0], None
            else:
                print("No hay salas activas con camas disponibles.")
                return None, None
    except Exception as e:
        log_message(f"[Error] {str(e)}")
        return None, None
import sqlite3
import os
from utils.log import log_message, log_database
from models.node import procesar_consulta
from datetime import datetime


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

        # Mostrar las salas en formato de tabla manualmente
        headers = ["ID Sala", "Nombre", "IP", "Estado", "Es Maestro", "Capacidad Total", "Capacidad Disponible"]
        header_line = "{:<10} {:<20} {:<15} {:<10} {:<10} {:<18} {:<22}".format(*headers)
        print(header_line)
        print("=" * len(header_line))

        for sala in salas:
            print("{:<10} {:<20} {:<15} {:<10} {:<10} {:<18} {:<22}".format(*sala))
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo listar las salas de emergencia: {e}")


def activar_sala(ip):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "UPDATE salas_emergencia SET estado = 'activada' WHERE ip = ?"
            cursor.execute(query, (ip,))
            conn.commit()
            
            log_database(f"# UPDATE salas_emergencia SET estado = 'activada' WHERE ip = '{ip}'")
            log_message(f"[Consulta] Activación de sala de emergencia con IP '{ip}' guardada en la base de datos.")

            cursor.execute("SELECT * FROM salas_emergencia WHERE ip = ?", (ip,))
            nodo_propio = cursor.fetchone()

            mensaje = f"UPDATE salas_emergencia SET estado = 'activada' WHERE ip = '{ip}'"

            procesar_consulta(mensaje)
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo activar la sala: {e}")

def obtener_sala_y_cama():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Selecciona la sala activa con la mayor proporción de camas disponibles
            cursor.execute("""
                SELECT salas_emergencia.id_sala 
                FROM salas_emergencia
                LEFT JOIN camas ON salas_emergencia.id_sala = camas.id_sala
                WHERE salas_emergencia.estado = 'activada' AND camas.estado = 'disponible'
                GROUP BY salas_emergencia.id_sala, salas_emergencia.capacidad_total
                HAVING salas_emergencia.capacidad_total > 0
                ORDER BY (CAST(COUNT(camas.id_cama) AS REAL) / salas_emergencia.capacidad_total) DESC
                LIMIT 1;
            """)
            sala = cursor.fetchone()

            print("Sala encontrada:", sala)  # Debug

            if sala:
                # Selecciona la primera cama disponible de la sala encontrada
                cursor.execute("""
                    SELECT id_cama 
                    FROM camas 
                    WHERE id_sala = ? AND estado = ? 
                    LIMIT 1
                """, (sala[0], 'disponible'))
                cama = cursor.fetchone()

                print("Cama encontrada:", cama)  # Debug

                if cama:
                    return sala[0], cama[0]
                else:
                    return sala[0], None
            else:
                return None, None
    except sqlite3.Error as e:
        log_message(f"[Error] {str(e)}")
        return None, None

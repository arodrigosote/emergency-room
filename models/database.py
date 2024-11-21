import sqlite3
from utils.log import log_message

def execute_query(query: str) -> bool:
    try:
        # Asumiendo que la conexión a la base de datos es a través de sqlite3
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        log_message(f"Query ejecutada con éxito: {query}")
        return True
    except Exception as e:
        log_message(f"Error ejecutando query: {e}")
        return False

import sqlite3

def actualizar_nodo_maestro(ip):
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        # Resetear la columna es_maestro
        cursor.execute("UPDATE salas_emergencia SET es_maestro = 0")
        
        # Actualizar la sala de emergencia con el nuevo nodo maestro
        cursor.execute("UPDATE salas_emergencia SET es_maestro = 1 WHERE ip = ?", (ip,))
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[Error] No se pudo actualizar el nodo maestro en la base de datos: {e}")

def obtener_nodo_maestro():
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        # Obtener el nodo maestro
        cursor.execute("SELECT * FROM salas_emergencia WHERE es_maestro = 1")
        nodo_maestro = cursor.fetchone()
        
        conn.close()
        
        if nodo_maestro:
            print(f"Nodo Maestro: ID={nodo_maestro[0]}, Nombre={nodo_maestro[1]}, IP={nodo_maestro[2]} Es maestro={nodo_maestro[3]}")
        
        return nodo_maestro
    except sqlite3.Error as e:
        print(f"[Error] No se pudo obtener el nodo maestro de la base de datos: {e}")
        return None
from controllers.server_client import active_connections
import sqlite3

def enviar_mensaje_a_nodo(mensaje, nodo_id):
    try:
        destino = int(nodo_id)
        if destino in active_connections:
            client_socket = active_connections[destino]
            if client_socket.fileno() != -1:  # Verifica que el socket siga activo
                client_socket.send(mensaje.encode())
                print(f"[Mensaje enviado] A nodo {destino}: {mensaje}")
                # Registrar el mensaje en la base de datos
                registrar_mensaje(destino, mensaje)
            else:
                print(f"[Error] La conexión con el nodo {destino} no está activa.")
        else:
            print(f"[Error] Nodo {destino} no está conectado.")
    except Exception as e:
        print(f"[Error] No se pudo enviar el mensaje: {e}")

def enviar_mensaje_a_todos(mensaje):
    for destino, client_socket in active_connections.items():
        try:
            if client_socket.fileno() != -1:  # Verifica que el socket siga activo
                client_socket.send(mensaje.encode())
                print(f"[Mensaje enviado] A nodo {destino}: {mensaje}")
                # Registrar el mensaje en la base de datos
                registrar_mensaje(destino, mensaje)
            else:
                print(f"[Error] La conexión con el nodo {destino} no está activa.")
        except Exception as e:
            print(f"[Error] No se pudo enviar el mensaje a nodo {destino}: {e}")

def registrar_mensaje(nodo_id, mensaje):
    # Registra el mensaje en la base de datos
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO registros (nodo_id, mensaje)
        VALUES (?, ?)
    ''', (nodo_id, mensaje))
    conn.commit()
    conn.close()
import sqlite3
import socket
import threading
import os
from datetime import datetime
from utils.log import log_message
from models.master_node import actualizar_nodo_maestro
from models.database import execute_query
from controllers.nodes import get_network_nodes

DB_PATH = 'nodos.db'

# Diccionario para conexiones activas
active_connections = {}
master_node = None
stop_event = threading.Event()  # Evento para controlar la terminación de hilos


def get_db_connection():
    """Obtiene una conexión a la base de datos."""
    return sqlite3.connect(DB_PATH)


def handle_client(client_socket, addr):
    """Maneja la conexión con un cliente."""
    try:
        log_message(f"[Servidor] Conexión establecida con {addr}")
        while not stop_event.is_set():
            data = client_socket.recv(1024)
            if not data:
                break
            mensaje_completo = data.decode()

            if mensaje_completo[:2] == "ex":
                break
            elif mensaje_completo[:2] == "01":
                connect_to_all_nodes()
                client_socket.send("OK".encode())
            elif mensaje_completo[:2] == "10":
                _, hora_actual, query = mensaje_completo.split("|")
                log_message(f"[Cliente Query] Recibido: {hora_actual} - {query}")
                resultado = execute_query(query)
                client_socket.send(("OK" if resultado else "Error").encode())
            elif mensaje_completo == "ping":
                client_socket.send("pong".encode())
            else:
                log_message(f"[Error] Código desconocido: {mensaje_completo}")
    except Exception as e:
        log_message(f"[Error] Cliente {addr}: {e}")
    finally:
        client_socket.close()
        log_message(f"[Servidor] Conexión cerrada con {addr}")


def start_server():
    """Inicia el servidor."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", 9999))
        server.listen(15)
        log_message("[Servidor] Escuchando en el puerto 9999")

        while not stop_event.is_set():
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
    except Exception as e:
        log_message(f"[Error] Problema al iniciar el servidor: {e}")
    finally:
        server.close()
        stop_event.set()


def connect_to_node(node):
    """Conecta con un nodo específico."""
    node_id = int(node['id'])
    node_ip = node['ip']
    if node_id in active_connections:
        return None

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        log_message(f"[Conectar Nodo] Intentando conectar con {node_ip}")
        client.connect((node_ip, 9999))
        active_connections[node_id] = client
        client.send("01|Conexión establecida".encode())
        log_message(f"[Conexión exitosa] Nodo {node_id} conectado")
    except Exception as e:
        log_message(f"[Error] No se pudo conectar con {node_ip}: {e}")
    finally:
        if node_id not in active_connections:
            client.close()


def connect_to_all_nodes():
    """Conecta a todos los nodos de la red."""
    nodes = get_network_nodes()
    for node in nodes:
        threading.Thread(target=connect_to_node, args=(node,), daemon=True).start()


def elegir_nodo_maestro():
    """Selecciona el nodo maestro basado en los nodos activos."""
    global master_node
    if active_connections:
        master_node_id = max(active_connections.keys())
        master_node_ip = active_connections[master_node_id].getpeername()[0]
        master_node = {'id': master_node_id, 'ip': master_node_ip}
        log_message(f"[Nodo Maestro] Nodo {master_node_id} ({master_node_ip}) seleccionado.")
        actualizar_nodo_maestro(master_node_ip)


if __name__ == "__main__":
    try:
        threading.Thread(target=start_server, daemon=True).start()
        connect_to_all_nodes()
    except KeyboardInterrupt:
        stop_event.set()
        log_message("[Servidor] Apagando servidor...")

import socket
import threading
import os
from datetime import datetime
from utils.log import log_message
from models.master_node import actualizar_nodo_maestro
from models.database import execute_query, obtener_cambios_db, guardar_cambios_db_changestomake
from controllers.nodes import get_network_nodes, get_own_node


# Diccionario para mantener las conexiones activas
active_connections = {}
master_node = None

def start_server():
    # Inicia el servidor y maneja solicitudes de clientes
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", 9999))
        server.listen(15)
        
        # Crear la carpeta 'history' si no existe
        os.makedirs('history', exist_ok=True)
        # Obtener la fecha y hora actual
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Mensaje a escribir en el archivo
        message = f"{timestamp} - [Servidor] Escuchando en el puerto 9999\n"
        # Escribir el mensaje en el archivo 'server_log.txt' dentro de la carpeta 'history'
        with open('history/server_log.txt', 'a') as log_file:
            log_file.write(message)

        elegir_nodo_maestro() 

        from controllers.handle_client import handle_client
        while True:
            client_socket, addr = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
            client_handler.start()
    except OSError as e:
        if "Address already in use" in str(e):
            log_message("[Error] El puerto 9999 ya está en uso. Liberando...")
            server.close()
            # Liberar conexiones activas
            for conn in active_connections.values():
                conn.close()
            active_connections.clear()
            start_server()  # Intentar reiniciar el servidor
        else:
            log_message(f"[Error] Problema al iniciar el servidor: {e}")
    except Exception as e:
        log_message(f"[Error] Error desconocido al iniciar el servidor: {e}")
    finally:
        server.close()

def connect_to_node(node):
    """
    Conecta con un nodo específico dado su dirección IP.
    """
    # Generar un ID basado en la IP
    node_id = int(node['id'])
    node_ip = node['ip']
    if node_id in [1, 2, 254]:  # Opcional: omitir nodos específicos
        return None

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        log_message(f"[Intentando conectar] Nodo IP: {node_ip}")
        client.connect((node_ip, 9999))

        # Verificar si el nodo ya está conectado
        if node_id in active_connections:
            log_message(f"[Info] Nodo {node_id} ya está conectado.")
            client.close()  # Cerrar la conexión redundante
            return

        # Almacenar la conexión activa
        active_connections[node_id] = client

        # Enviar mensaje de conexión con código de instrucción
        instruction_code = "01"
        message = f"{instruction_code} Hola, soy un nodo nuevo en el sistema"
        client.send(message.encode())
        log_message(f"[Conexión exitosa] Nodo {node_id} conectado. Activas: {list(active_connections.keys())}")

        # Actualizar el nodo maestro
        elegir_nodo_maestro()

        log_message(f"[Actualizar base de datos] Esperando respuesta de nodo {node_id} ...")
        data = client.recv(1024).decode()

        if data == "OK":
            log_message(f"[Respuesta recibida] De nodo {node_id}: {data}")

    except Exception as e:
        log_message(f"[Error] No se pudo conectar con el nodo {node_ip}: {e}")
    finally:
        # Asegurarse de cerrar la conexión si no se almacenó correctamente
        if node_id not in active_connections:
            client.close()


def mostrar_conexiones():
    # Muestra las conexiones activas
    log_message("[Conexiones activas]:")
    for node_id in active_connections.keys():
        log_message(f"ID: {node_id}")

def elegir_nodo_maestro():
    global master_node
    if active_connections:
        master_node_id = max(active_connections.keys())
        master_node_ip = active_connections[master_node_id].getpeername()[0]
        master_node = {'id': master_node_id, 'ip': master_node_ip}
        log_message(f"[Nodo Maestro] Nodo {master_node['id']} con IP {master_node['ip']} es el nodo maestro.")
        actualizar_nodo_maestro(master_node_ip)
        return master_node

def get_client_socket_by_ip(ip):
    id = int(ip.split('.')[-1])
    return active_connections.get(id, None)
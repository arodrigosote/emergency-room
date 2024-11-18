import socket
import threading
from controllers.nodes import get_network_nodes
from datetime import datetime
import os
from utils.log import log_message
from models.master_node import actualizar_nodo_maestro

# Diccionario para mantener las conexiones activas
active_connections = {}
master_node = None



def handle_client(client_socket, addr):
    # Maneja la conexión con un cliente
    try:
        log_message(f"[Servidor] Conexión establecida con {addr}")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            if data.decode()[:2] == "ex":
                break
            elif data.decode()[:2] == "01":
                nodos = get_network_nodes()
                connect_clients(nodos)
                mostrar_conexiones()
                continue
            elif data.decode()[:2] == "ms":
                enviar_mensaje()
                continue
            
            log_message(f"[Mensaje recibido] De {addr}: {data.decode()}")
            response = f"Servidor recibió: {data.decode()}"
            client_socket.send(response.encode())
    except Exception as e:
        log_message(f"[Error] Cliente {addr}: {e}")
    finally:
        client_socket.close()
        log_message(f"[Servidor] Conexión cerrada con {addr}")

def start_server():
    # Inicia el servidor y maneja solicitudes de clientes
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", 9999))
        server.listen(15)
        
        # Crear la carpeta 'history' si no existe
        if not os.path.exists('history'):
            os.makedirs('history')
        # Obtener la fecha y hora actual
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        # Mensaje a escribir en el archivo
        message = f"{timestamp} - [Servidor] Escuchando en el puerto 9999\n"
         # Escribir el mensaje en el archivo 'server_log.txt' dentro de la carpeta 'history'
        with open('history/server_log.txt', 'a') as log_file:
            log_file.write(message)

        elegir_nodo_maestro()
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

def connect_clients(nodes):
    # Conecta con los nodos de la red
    for node in nodes:
        node_id = int(node['id'])
        if node_id in [1, 2, 254]:  # Opcional: omitir nodos específicos
            continue

        if node_id in active_connections:
            log_message(f"[Info] Nodo {node_id} ya está conectado.")
            continue

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            log_message(f"[Intentando conectar] Nodo ID: {node_id}, IP: {node['ip']}")
            client.connect((node['ip'], 9999))
            active_connections[node_id] = client  # Almacena la conexión activa

            # Enviar mensaje de conexión con código de instrucción
            instruction_code = "01"
            message = f"{instruction_code} Hola, soy un nodo nuevo en el sistema"
            client.send(message.encode())
            elegir_nodo_maestro()
            log_message(f"[Conexión exitosa] Nodo {node_id} conectado. Activas: {list(active_connections.keys())}")
        except Exception as e:
            log_message(f"[Error] No se pudo conectar con el nodo {node['ip']}: {e}")
        finally:
            if node_id not in active_connections:
                client.close()  # Asegurarse de cerrar conexiones fallidas


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
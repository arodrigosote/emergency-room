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
conexiones_inactivas = []  # Lista para almacenar nodos inactivos

def handle_client(client_socket, addr):
    # Maneja la conexión con un cliente
    try:
        log_message(f"[Servidor] Conexión establecida con {addr}")
        while True:
            data = client_socket.recv(1024)
            mensaje_completo = data.decode()
            
            if not data:
                break
            if mensaje_completo[:2] == "ex":
                break
            elif mensaje_completo[:2] == "01":
                nodos = get_network_nodes()
                for node in nodos:
                    node_id = node.get("id")  
                    if node_id not in active_connections:
                        conn = connect_to_node(node)
                        if conn:
                            active_connections[node_id] = conn

                client_socket.send("OK".encode())
                continue
            elif mensaje_completo[:2] == "10":
                codigo_instruccion, hora_actual, query = mensaje_completo.split("|")
                log_message(f"[Cliente Query] Recibido: {hora_actual} - {query}")

                resultado = execute_query(query)
                response = "OK" if resultado else "Error"
                log_message(f"[Cliente Query] Ejecutada - Estatus: {response} - {query}")
                client_socket.send(response.encode())
                continue
            elif mensaje_completo[:2] == "11":
                codigo_instruccion, hora_actual, query = mensaje_completo.split("|")
                mensaje_nuevo = f"10|{hora_actual}|{query}"
                respuestas = []
                nodo_emisor = client_socket
                # log_message('[Nodo Maestro] Recibe mensaje')
                for destino, client in active_connections.items():
                    try:
                        if client.fileno() != -1:  # Verifica que el socket siga activo
                            client.send(mensaje_nuevo.encode())
                            log_message(f"[Master Mensaje enviado] A nodo {destino}: {mensaje_nuevo}")

                            # Analizar la respuesta del servidor
                            respuesta = client.recv(1024).decode()  
                            log_message(f"[Master Respuesta recibida] De nodo {destino}: {respuesta}")
                            respuestas.append(respuesta)
                        else:
                            log_message(f"[Error] La conexión con el nodo {destino} no está activa.")
                    except Exception as e:
                        log_message(f"[Error] No se pudo enviar el mensaje a nodo {destino}: {e}")

                # Verificar si todas las respuestas son "OK"
                if all(respuesta == "OK" for respuesta in respuestas):
                    response = "OK"
                    log_message(f"[Master Consenso] Query Ejecutada: Estatus: {response} - {query}")
                else:
                    response = "Error"
                nodo_emisor.send(response.encode())
                continue
            elif mensaje_completo[:2] == "12":
                try:

                    # Crear la carpeta 'database' si no existe
                    os.makedirs("history", exist_ok=True)
                    # log_message("[Info] Carpeta 'history' creada o ya existente.")

                    # Ruta del archivo
                    archivo_path = os.path.join("history", "db_changes.txt")

                    # Leer el contenido del archivo db_changes
                    with open(archivo_path, 'r') as file:
                        db_changes = file.read()

                    # Enviar el contenido del archivo como respuesta
                    client_socket.send(db_changes.encode())
                    log_message("[Cliente Mensaje enviado] Contenido del archivo 'db_changes' enviado.")

                except FileNotFoundError:
                    log_message("[Error] El archivo 'db_changes' no se encontró en la carpeta 'history'")
                    client_socket.send("[Error] El archivo 'db_changes' no se encontró.".encode())
                except Exception as e:
                    log_message(f"[Error] No se pudo procesar el mensaje '12': {e}")
                    client_socket.send(f"[Error] No se pudo procesar el mensaje '12': {e}".encode())
                continue
            elif mensaje_completo[:2] == "13":
                codigo_instruccion, hora_actual, query = mensaje_completo.split("|")
                mensaje_nuevo = f"12|{hora_actual}|{query}"
                respuestas = []
                nodo_emisor = client_socket
                # log_message('[Nodo Maestro] Recibe mensaje')
                for destino, client in active_connections.items():
                    try:
                        if client.fileno() != -1:  # Verifica que el socket siga activo
                            client.send(mensaje_nuevo.encode())
                            log_message(f"[Master Mensaje enviado] A nodo {destino}: {mensaje_nuevo}")

                            # Analizar la respuesta del servidor
                            respuesta = client.recv(1024).decode()  
                            log_message(f"[Master Respuesta recibida] De nodo {destino}: {respuesta}")
                            respuestas.append(respuesta)
                        else:
                            log_message(f"[Error] La conexión con el nodo {destino} no está activa.")
                    except Exception as e:
                        log_message(f"[Error] No se pudo enviar el mensaje a nodo {destino}: {e}")

                if codigo_instruccion == "13":
                    respuestas_texto = "\n".join(respuestas)
                    nodo_emisor.send(respuestas_texto.encode())
                
                # Verificar si todas las respuestas son "OK"
                if all(respuesta == "OK" for respuesta in respuestas):
                    response = "OK"
                    log_message(f"[Master Consenso] Query Ejecutada: Estatus: {response} - {query}")
                else:
                    response = "Error"
                nodo_emisor.send(response.encode())
                continue
            elif mensaje_completo == "ping":
                client_socket.send("pong".encode())
                continue
            else:
                log_message("[Error] No se encontró el código de instrucción")
                log_message(mensaje_completo)
                break
    except Exception as e:
        log_message(f"[Error] Cliente {mensaje_completo[:2]} {addr}: {e}")
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

def verificar_conexiones():
    """
    Verifica las conexiones activas enviando un mensaje de prueba.
    Si la conexión está inactiva, elimina el nodo de la lista de conexiones activas.
    """
    log_message("[Verificación] Iniciando verificación de conexiones...")

    for node_id, client in list(active_connections.items()):
        try:
            # Intentamos enviar un mensaje de prueba
            client.send(b"ping")
        except (socket.error, OSError) as e:
            # Si hay un error, la conexión está inactiva
            log_message(f"[Conexión perdida] Nodo {node_id}. Error: {e}")
            print(f"[Conexión perdida] Nodo {node_id}. Error: {e}")
            conexiones_inactivas.append(node_id)
            client.close()  # Cerramos el socket inactivo
            elegir_nodo_maestro()

    # Eliminar nodos inactivos del diccionario de conexiones activas
    for node_id in conexiones_inactivas:
        del active_connections[node_id]
        log_message(f"[Conexión eliminada] Nodo {node_id} eliminado del diccionario de conexiones activas.")



    

import socket
import threading
import os
from datetime import datetime
from utils.log import log_message
from models.master_node import actualizar_nodo_maestro
from models.database import execute_query, obtener_cambios_db, guardar_cambios_db_changestomake
from controllers.nodes import get_network_nodes, get_own_node
from controllers.server_client import active_connections

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
                print('Server recibe solicitud nueva')
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
                log_message(f"[Query] Recibido: {hora_actual} - {query}")

                resultado = execute_query(query)
                response = "OK" if resultado else "Error"
                log_message(f"[Query] Ejecutada - Estatus: {response} - {query}")
                client_socket.send(response.encode())
                continue
            elif mensaje_completo[:2] == "11":
                codigo_instruccion, hora_actual, query = mensaje_completo.split("|")
                mensaje_nuevo = f"10|{hora_actual}|{query}"
                respuestas = []
                nodo_emisor = client_socket
                log_message('[Nodo Maestro] Recibe mensaje')
                for destino, client in active_connections.items():
                    try:
                        if client.fileno() != -1:  # Verifica que el socket siga activo
                            client.send(mensaje_nuevo.encode())
                            log_message(f"[Mensaje enviado] A nodo {destino}: {mensaje_nuevo}")

                            # Analizar la respuesta del servidor
                            respuesta = client.recv(1024).decode()  
                            log_message(f"[Respuesta recibida] De nodo {destino}: {respuesta}")
                            respuestas.append(respuesta)
                        else:
                            log_message(f"[Error] La conexión con el nodo {destino} no está activa.")
                    except Exception as e:
                        log_message(f"[Error] No se pudo enviar el mensaje a nodo {destino}: {e}")

                # Verificar si todas las respuestas son "OK"
                response = "OK" if all(respuesta == "OK" for respuesta in respuestas) else "Error"
                log_message(f"[Query] Ejecutada: Estatus: {response} - {query}")
                nodo_emisor.send(response.encode())
                continue
            elif mensaje_completo[:2] == "12":
                try:
                    print('[Recibiendo solicitud de cambios]')

                    # Crear la carpeta 'database' si no existe
                    os.makedirs("history", exist_ok=True)
                    log_message("[Info] Carpeta 'history' creada o ya existente.")

                    # Ruta del archivo
                    archivo_path = os.path.join("history", "db_changes.txt")

                    # Leer el contenido del archivo db_changes
                    with open(archivo_path, 'r') as file:
                        db_changes = file.read()

                    # Enviar el contenido del archivo como respuesta
                    client_socket.send(db_changes.encode())
                    log_message("[Mensaje enviado] Contenido del archivo 'db_changes' enviado al cliente.")

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
                log_message('[Nodo Maestro] Recibe mensaje')
                for destino, client in active_connections.items():
                    try:
                        if client.fileno() != -1:  # Verifica que el socket siga activo
                            client.send(mensaje_nuevo.encode())
                            log_message(f"[Mensaje enviado] A nodo {destino}: {mensaje_nuevo}")

                            # Analizar la respuesta del servidor
                            respuesta = client.recv(1024).decode()  
                            log_message(f"[Respuesta recibida] De nodo {destino}: {respuesta}")
                            respuestas.append(respuesta)
                        else:
                            log_message(f"[Error] La conexión con el nodo {destino} no está activa.")
                    except Exception as e:
                        log_message(f"[Error] No se pudo enviar el mensaje a nodo {destino}: {e}")

                if codigo_instruccion == "13":
                    respuestas_texto = "\n".join(respuestas)
                    nodo_emisor.send(respuestas_texto.encode())
                
                # Verificar si todas las respuestas son "OK"
                response = "OK" if all(respuesta == "OK" for respuesta in respuestas) else "Error"
                log_message(f"[Query] Ejecutada: Estatus: {response} - {query}")
                nodo_emisor.send(response.encode())
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

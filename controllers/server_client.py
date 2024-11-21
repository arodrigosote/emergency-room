import socket
import threading
import os
from datetime import datetime
from utils.log import log_message
from models.master_node import actualizar_nodo_maestro
from models.database import execute_query
# from models.emergency_room import activar_sala  # Mover esta importación dentro de la función
from controllers.nodes import get_network_nodes, get_own_node


# Diccionario para mantener las conexiones activas
active_connections = {}
master_node = None


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

                #envia cambios de base de datos a nuevas conexiones
                connect_clients_send_dbchanges(nodos)
                mostrar_conexiones()
                continue
            elif mensaje_completo[:2] == "10":
                codigo_instruccion, hora_actual, query = mensaje_completo.split("|")
                log_message(f"[Query] Recibido: {hora_actual} - {query}")
                resultado = execute_query(query)
                hora_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if resultado:
                    response = f"OK"
                    log_message(f"[Query] Ejecutada: {hora_ejecucion} Estatus: {response} - {query}")
                else:
                    response = f"Error"
                    log_message(f"[Query] Recibido: {hora_ejecucion} Estatus: {response} - {query}")
                client_socket.send(response.encode())
                
                continue
            elif mensaje_completo[:2] == "11":
                codigo_instruccion, hora_actual, query = mensaje_completo.split("|")
                mensaje_nuevo = f"10|{hora_actual}|{query}"
                respuestas = []
                for destino, client_socket in active_connections.items():
                    try:
                        if client_socket.fileno() != -1:  # Verifica que el socket siga activo
                            client_socket.send(mensaje_nuevo.encode())
                            log_message(f"[Mensaje enviado] A nodo {destino}: {mensaje_nuevo}")
                            
                            # Analizar la respuesta del servidor
                            respuesta = client_socket.recv(1024).decode()  # Tamaño del buffer ajustable
                            log_message(f"[Respuesta recibida] De nodo {destino}: {respuesta}")
                            respuestas.append(respuesta)
                            
                        else:
                            log_message(f"[Error] La conexión con el nodo {destino} no está activa.")
                    except Exception as e:
                        log_message(f"[Error] No se pudo enviar el mensaje a nodo {destino}: {e}")

                # Verificar si todas las respuestas son "OK"
                if all(respuesta == "OK" for respuesta in respuestas):
                    log_message("[Consenso] Todos los nodos respondieron OK")
                    response = f"OK"
                    log_message(f"[Query] Ejecutada: {hora_ejecucion} Estatus: {response} - {query}")
                else:
                    log_message("[Sin consenso] No todos los nodos respondieron OK")
                    response = f"Error"
                    log_message(f"[Query] Recibido: {hora_ejecucion} Estatus: {response} - {query}")
                
                client_socket.send(response.encode())              
                
                continue

            elif mensaje_completo[:2] == "12":
                try:
                # Crear la carpeta 'database' si no existe
                    os.makedirs("database", exist_ok=True)
                    log_message("[Info] Carpeta 'database' creada o ya existente.")

                    # Ruta del archivo
                    archivo_path = os.path.join("database", "changestomake.txt")

                    # Dividir el texto en líneas
                    lineas = mensaje_completo.splitlines()

                    # Procesar las líneas y guardar las consultas válidas
                    with open(archivo_path, "w") as archivo:
                        for linea in lineas:
                            linea = linea.strip()
                            if "#" in linea:
                                # Separar la fecha y hora de la consulta
                                partes = linea.split("#", 1)
                                fecha_hora = partes[0].strip()[:-2]
                                consulta = partes[1].strip()

                                # Eliminar el guion antes de la consulta (si existe)
                                consulta = consulta.replace(" - ", " ")

                                # Validar formato de fecha y hora (opcional)
                                try:
                                    datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
                                    # Escribir en el archivo
                                    archivo.write(f"{fecha_hora}#{consulta}\n")
                                    log_message(f"[Info] Consulta guardada: {fecha_hora} {consulta}")
                                except ValueError:
                                    log_message(f"[Error] Formato de fecha y hora no válido: {fecha_hora}")
                except Exception as e:
                    log_message(f"[Error] No se pudo procesar el mensaje '12': {e}")
                
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



def connect_clients_send_dbchanges(nodes):
    # Conecta con los nodos de la red y envía los cambios de la base de datos
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
            elegir_nodo_maestro()
            # Leer el contenido del archivo db_changes
            try:
                with open('history/db_changes.txt', 'r') as file:
                    db_changes = file.read()
                # Enviar los cambios de la base de datos con código de instrucción "12"
                instruction_code = "12"
                message = f"{instruction_code}\n{db_changes}"
                client.send(message.encode())
                log_message(f"[Mensaje enviado] Cambios de la base de datos enviados a nodo {node_id}")
            except FileNotFoundError:
                log_message("[Error] El archivo 'db_changes' no se encontró en la carpeta 'history'")
            except Exception as e:
                log_message(f"[Error] No se pudo leer el archivo 'db_changes': {e}")

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

def get_client_socket_by_ip(ip):
    # ...existing code...
    id = ip.split('.')[-1]
    for node_id, client_socket in active_connections.items():
        print(node_id, client_socket)
        print(int(node_id) == int(id))
        if int(node_id) == int(id):
            return client_socket
    return None
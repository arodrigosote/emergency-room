import sqlite3
from datetime import datetime
from utils.log import log_message
from controllers.server_client import get_client_socket_by_ip, active_connections  # Asegúrate de tener una función para obtener el socket del cliente
from controllers.nodes import get_network_nodes, get_own_node


def obtener_nodo_propio(cursor, own_node_ip):
    cursor.execute("SELECT * FROM salas_emergencia WHERE ip = ?", (own_node_ip,))
    return cursor.fetchone()

def enviar_mensaje(client_socket, codigo, mensaje):
    """Envía un mensaje a un cliente y maneja la respuesta."""
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_completo = f"{codigo}|{hora_actual}|{mensaje}"

    try:
        if client_socket.fileno() != -1:  # Verifica que el socket siga activo
            client_socket.send(mensaje_completo.encode())
            log_message(f"[Mensaje enviado] {mensaje_completo}")
            respuesta = client_socket.recv(1024).decode()
            log_message(f"[Respuesta recibida] {respuesta}")
            return respuesta
        else:
            log_message("[Error] Conexión inactiva.")
            return None
    except Exception as e:
        log_message(f"[Error al enviar] {str(e)}")
        return None
    

def enviar_mensajes_a_todos(codigo, mensaje, incluir_propio=False):
    """Envía un mensaje a todos los nodos conectados."""
    respuestas = []
    own_node_ip = get_own_node()['ip']

    for destino_id, client_socket in active_connections.items():
        try:
            destino_ip = client_socket.getpeername()[0]

            if incluir_propio or destino_ip != own_node_ip:
                respuesta = enviar_mensaje(client_socket, codigo, mensaje)
                if respuesta:
                    respuestas.append(respuesta)
        except Exception as e:
            log_message(f"[Error] No se pudo enviar mensaje al nodo {destino_id}: {str(e)}")

    if codigo == "12":
        return respuestas

    if all(res == "OK" for res in respuestas):
        log_message("[Consenso] Todos los nodos respondieron OK.")
    else:
        log_message("[Sin consenso] No todos los nodos respondieron OK.")

def procesar_consulta(consulta, es_compleja=False):
    """Procesa consultas simples o complejas dependiendo del tipo."""
    try:
        master_node_id = max(active_connections.keys())
        master_node_ip = active_connections[master_node_id].getpeername()[0]
        own_node = get_own_node()

        with sqlite3.connect('nodos.db') as conn:
            cursor = conn.cursor()
            nodo_propio = obtener_nodo_propio(cursor, own_node['ip'])

            if not nodo_propio:
                log_message("[Nodo Propio] Nodo no encontrado en la base de datos.")
                return

            if nodo_propio[2] == master_node_ip:
                log_message("[Nodo] Este nodo es el maestro.")
                from models.emergency_room import obtener_sala_y_cama
                if es_compleja:
                    sala, cama = obtener_sala_y_cama()
                    if sala and cama:
                        consulta = consulta.replace("00", str(sala)).replace("01", str(cama))
                        enviar_mensajes_a_todos("10", consulta, incluir_propio=True)
                    else:
                        log_message("[Error] No hay camas disponibles.")
                else:
                    enviar_mensajes_a_todos("10", consulta, incluir_propio=True)

            else:
                log_message("[Nodo] Nodo maestro remoto detectado.")
                master_socket = active_connections[master_node_id]
                enviar_mensaje(master_socket, "11", consulta)

    except Exception as e:
        log_message(f"[Error] {str(e)}")

def solicitar_cambios_db():
    """Procesa consultas simples o complejas dependiendo del tipo."""
    try:
        master_node_id = max(active_connections.keys())
        master_node_ip = active_connections[master_node_id].getpeername()[0]
        own_node = get_own_node()

        with sqlite3.connect('nodos.db') as conn:
            cursor = conn.cursor()
            nodo_propio = obtener_nodo_propio(cursor, own_node['ip'])

            if not nodo_propio:
                log_message("[Nodo Propio] Nodo no encontrado en la base de datos.")
                return

            if nodo_propio[2] == master_node_ip:
                log_message("[Soliitar cambios] Este nodo es el maestro.")
                respuestas = enviar_mensajes_a_todos("12", "Solicitar cambios en la base de datos.", incluir_propio=True)
                print(respuestas)
                log_message("[Solicitar cambios] Se han solicitado los cambios en la base de datos.")
            else:
                log_message("[Nodo] Nodo maestro remoto detectado.")
                master_socket = active_connections[master_node_id]
                respuestas = enviar_mensaje(master_socket, "13", "Solicitar cambios en la base de datos.")
                print(respuestas)

    except Exception as e:
        log_message(f"[Error] {str(e)}")
# def enviar_consulta_sencilla(consulta):
#     try:
#         master_node_id = max(active_connections.keys())
#         master_node_ip = active_connections[master_node_id]
#         own_node = get_own_node()

#         with sqlite3.connect('nodos.db') as conn:
#             cursor = conn.cursor()
#             nodo_propio = obtener_nodo_propio(cursor, own_node['ip'])

#             if nodo_propio:
#                 if nodo_propio[2] == master_node_ip:
#                     log_message("[Nodo] El nodo propio es el nodo maestro.")
#                     enviar_mensaje_a_todos("10", consulta)
#                 else:
#                     log_message("[Nodo] El nodo propio no es el nodo maestro.")
#                     enviar_mensaje_a_maestro(master_node_ip, "11", consulta)
#             else:
#                 log_message("\n[Nodo Propio] No se encontró el nodo propio.")
#     except Exception as e:
#         log_message(f"[Error] {str(e)}")

# def enviar_consulta_compleja(consulta):
#     try:
#         master_node_id = max(active_connections.keys())
#         master_node_ip = active_connections[master_node_id].getpeername()[0]
#         master = active_connections[master_node_id]
#         own_node = get_own_node()

#         with sqlite3.connect('nodos.db') as conn:
#             cursor = conn.cursor()
#             nodo_propio = obtener_nodo_propio(cursor, own_node['ip'])

#             if nodo_propio:
#                 if nodo_propio[2] == master_node_ip:
#                     sala, cama = obtener_sala_y_cama()
#                     if sala and cama:
#                         consulta = consulta.replace("00", str(sala)).replace("01", str(cama))
#                         log_message("[Nodo] El nodo propio es el nodo maestro.")
#                         enviar_mensaje_a_todos_incluyendo_propio("10", consulta)
#                         log_message(f"[Nodo] Se asignó la cama {cama} en la sala {sala} al paciente.")
#                     else:
#                         log_message("[Nodo] No hay camas disponibles en ninguna sala.")
#                         print("No hay camas disponibles en ninguna sala.")
#                 else:
#                     log_message("[Nodo] El nodo propio no es el nodo maestro.")
#                     enviar_mensaje_a_maestro_calculo_sala(master, "11", consulta)
#             else:
#                 log_message("\n[Nodo Propio] No se encontró el nodo propio.")
#     except Exception as e:
#         log_message(f"[Error] {str(e)}")



# def enviar_mensaje_a_todos(codigo_instruccion, mensaje):
#     hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     mensaje_completo = f"{codigo_instruccion}|{hora_actual}|{mensaje}"
#     respuestas = []
#     own_node = get_own_node()
    
#     for destino, client_socket in active_connections.items():
#         try:
#             # Obtener la IP del nodo destino
#             destino_ip = client_socket.getpeername()[0]
            
#             # Verificar que el nodo destino no sea el nodo propio
#             if destino_ip != own_node['ip']:
#                 if client_socket.fileno() != -1:  # Verifica que el socket siga activo
#                     client_socket.send(mensaje_completo.encode())
#                     log_message(f"[Mensaje enviado] A nodo {destino}: {mensaje_completo}")
                    
#                     # Analizar la respuesta del servidor
#                     respuesta = client_socket.recv(1024).decode()  # Tamaño del buffer ajustable
#                     log_message(f"[Respuesta recibida] De nodo {destino}: {respuesta}")
#                     respuestas.append(respuesta)
#                 else:
#                     log_message(f"[Error] La conexión con el nodo {destino} no está activa.")
#             else:
#                 log_message(f"[Nodo Propio] No se envía mensaje al nodo propio.")
#         except Exception as e:
#             log_message(f"[Error] No se pudo enviar el mensaje a nodo {destino}: {e}")
    
#     # Verificar si todas las respuestas son "OK"
#     if all(respuesta == "OK" for respuesta in respuestas):
#         log_message("[Consenso] Todos los nodos respondieron OK")
#     else:
#         log_message("[Sin consenso] No todos los nodos respondieron OK")

# def enviar_mensaje_a_todos_incluyendo_propio(codigo_instruccion, mensaje):
#     hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     mensaje_completo = f"{codigo_instruccion}|{hora_actual}|{mensaje}"
#     respuestas = []
#     own_node = get_own_node()
    
#     for destino, client_socket in active_connections.items():
#         try:            
#             # Verificar que el nodo destino no sea el nodo propio
#             if client_socket.fileno() != -1:  # Verifica que el socket siga activo
#                 client_socket.send(mensaje_completo.encode())
#                 log_message(f"[Mensaje enviado] A nodo {destino}: {mensaje_completo}")
                    
#                 # Analizar la respuesta del servidor
#                 respuesta = client_socket.recv(1024).decode()  # Tamaño del buffer ajustable
#                 log_message(f"[Respuesta recibida] De nodo {destino}: {respuesta}")
#                 respuestas.append(respuesta)
#             else:
#                 log_message(f"[Nodo Propio] No se envía mensaje al nodo propio.")
#         except Exception as e:
#             log_message(f"[Error] No se pudo enviar el mensaje a nodo {destino}: {e}")
    
#     # Verificar si todas las respuestas son "OK"
#     if all(respuesta == "OK" for respuesta in respuestas):
#         log_message("[Consenso] Todos los nodos respondieron OK")
#     else:
#         log_message("[Sin consenso] No todos los nodos respondieron OK")

        
# def enviar_mensaje_a_maestro(client, codigo, mensaje):
#     hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     mensaje_completo = f"{codigo}|{hora_actual}|{mensaje}"
#     #nodo_maestro = get_client_socket_by_ip(ip_nodo_maestro)  # Obtener el socket del nodo maestro usando su IP
#     try:
#         if client.fileno() != -1:  # Verifica que el socket siga activo
#             client.send(mensaje_completo.encode())
#             log_message(f"[Mensaje enviado] A nodo maestro: {mensaje_completo}")
            
#             # Analizar la respuesta del servidor
#             respuesta = client.recv(1024).decode()  # Tamaño del buffer ajustable
#             log_message(f"[Respuesta recibida] De nodo maestro: {respuesta}")
            
#             if respuesta == "OK":
#                 log_message("[Consenso] El nodo maestro respondió OK, Query ejecutada en todos nodos")
#             else:
#                 log_message("[Sin consenso] El nodo maestro no respondió OK, Error")
                
#         else:
#             log_message("[Error] La conexión con el nodo maestro no está activa.")
#     except Exception as e:
#         print(f"[Error] No se pudo enviar el mensaje al nodo maestro: {e}")
#         print(f"[Debug] Detalles del error: {str(e)}")
#         import traceback

# def enviar_mensaje_a_maestro_calculo_sala(master, codigo, mensaje):
#     hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     sala, cama = obtener_sala_y_cama()
#     if sala and cama:
#         # Reemplazar "00" con el valor de sala y "01" con el valor de cama
#         mensaje = mensaje.replace("00", str(sala)).replace("01", str(cama))
#     else:
#         log_message("[Nodo] No hay camas disponibles en ninguna sala.")
#         print("No hay camas disponibles en ninguna sala.")
#     mensaje_completo = f"{codigo}|{hora_actual}|{mensaje}"
#     try:
#         if master.fileno() != -1:  # Verifica que el socket siga activo
#             master.send(mensaje_completo.encode())
#             log_message(f"[Mensaje enviado] A nodo maestro: {mensaje_completo}")
            
#             # Analizar la respuesta del servidor
#             respuesta = master.recv(1024).decode()  # Tamaño del buffer ajustable
#             log_message(f"[Respuesta recibida] De nodo maestro: {respuesta}")
            
#             if respuesta == "OK":
#                 log_message("[Consenso] El nodo maestro respondió OK, Query ejecutada en todos nodos")
#             else:
#                 log_message("[Sin consenso] El nodo maestro no respondió OK, Error")
                
#         else:
#             log_message(f"[Error] La conexión con el nodo maestro no está activa.")
#     except Exception as e:
#         log_message(f"[Error] No se pudo enviar el mensaje al nodo maestro: {e}")
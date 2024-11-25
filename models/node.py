import sqlite3
from datetime import datetime
from utils.log import log_message
from controllers.server_client import get_client_socket_by_ip, active_connections, elegir_nodo_maestro
from controllers.nodes import get_network_nodes, get_own_node
from models.database import guardar_cambios_db_changestomake


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
    except (ConnectionResetError, BrokenPipeError) as e:
        log_message(f"[Error] Conexión perdida con el cliente: {str(e)}")
        # Aquí puedes agregar lógica para manejar la desconexión, como eliminar la conexión de active_connections
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
        respuestas_texto = "\n".join(respuestas)
        return respuestas_texto
        

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
                        enviar_mensajes_a_todos("10", consulta, incluir_propio=False)
                    else:
                        log_message("[Error] No hay camas disponibles.")
                else:
                    enviar_mensajes_a_todos("10", consulta, incluir_propio=False)

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
                guardar_cambios_db_changestomake(respuestas)
                log_message("[Solicitar cambios] Se han solicitado los cambios en la base de datos.")
            else:
                log_message("[Nodo] Nodo maestro remoto detectado.")
                master_socket = active_connections[master_node_id]
                respuestas = enviar_mensaje(master_socket, "13", "Solicitar cambios en la base de datos.")
                guardar_cambios_db_changestomake(respuestas)
                log_message("[Solicitar cambios] Se han solicitado los cambios en la base de datos.")

    except Exception as e:
        log_message(f"[Error] {str(e)}")

def verificar_conexiones():
    """Verifica las conexiones activas y recalcula el nodo maestro si es necesario."""
    conexiones_cerradas = []
    try:
        nodos_red = get_network_nodes()
        nodos_activos = list(active_connections.keys())

        for nodo_id in nodos_activos:
            try:
                client_socket = active_connections[nodo_id]
                if client_socket.fileno() == -1:  # Verifica si el socket sigue activo
                    raise ConnectionError("Socket inactivo.")
            except Exception as e:
                log_message(f"[Conexión perdida] Nodo {nodo_id}: {e}")
                conexiones_cerradas.append(nodo_id)
                client_socket.close()
                del active_connections[nodo_id]
                elegir_nodo_maestro()

    except Exception as e:
        log_message(f"[Error] {str(e)}")
    
    return conexiones_cerradas
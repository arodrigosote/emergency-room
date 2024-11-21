import sqlite3
from datetime import datetime
from utils.log import log_message
from controllers.server_client import get_client_socket_by_ip, active_connections  # Asegúrate de tener una función para obtener el socket del cliente
from controllers.nodes import get_network_nodes, get_own_node

def enviar_consulta(consulta):
    pass


def enviar_consulta_sencilla(consulta):

    # Obteniendo nodo maestro de conexiones activas
    master_node_id = max(active_connections.keys())
    master_node_ip = active_connections[master_node_id].getpeername()[0]
    own_node = get_own_node()

    # Conexion con la base de datos
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()

    # Obtener el nodo propio
    cursor.execute("SELECT * FROM salas_emergencia WHERE ip = ?", (own_node['ip'],))
    nodo_propio = cursor.fetchone()

    # Comprobar si el nodo propio es el maestro o no.
    if nodo_propio:
        # Comparar con el nodo maestro
        if nodo_propio[2] == master_node_ip:
            log_message("[Nodo] El nodo propio es el nodo maestro.")
            # Enviar mensaje a todos los nodos
            codigo = "10"
            enviar_mensaje_a_todos(codigo, consulta)
        else:
            log_message("[Nodo] El nodo propio no es el nodo maestro.")
            codigo = "11"
            enviar_mensaje_a_maestro(master_node_ip, codigo, consulta)
    else:
        log_message("\n[Nodo Propio] No se encontró el nodo propio.")



def enviar_mensaje_a_todos(codigo_instruccion, mensaje):
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_completo = f"{codigo_instruccion}|{hora_actual}|{mensaje}"
    respuestas = []
    for destino, client_socket in active_connections.items():
        try:
            if client_socket.fileno() != -1:  # Verifica que el socket siga activo
                client_socket.send(mensaje_completo.encode())
                log_message(f"[Mensaje enviado] A nodo {destino}: {mensaje_completo}")
                
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
    else:
        log_message("[Sin consenso] No todos los nodos respondieron OK")


def enviar_mensaje_a_maestro(ip_nodo_maestro, codigo, mensaje):
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_completo = f"{codigo}|{hora_actual}|{mensaje}"
    nodo_maestro = get_client_socket_by_ip(ip_nodo_maestro)  # Obtener el socket del nodo maestro usando su IP    
    print(nodo_maestro)
    try:
        if nodo_maestro.fileno() != -1:  # Verifica que el socket siga activo
            nodo_maestro.send(mensaje_completo.encode())
            print('mensaje enviado')
            log_message(f"[Mensaje enviado] A nodo maestro: {mensaje_completo}")
            
            # Analizar la respuesta del servidor
            respuesta = nodo_maestro.recv(1024).decode()  # Tamaño del buffer ajustable
            log_message(f"[Respuesta recibida] De nodo maestro: {respuesta}")
            
            if respuesta == "OK":
                log_message("[Consenso] El nodo maestro respondió OK, Query ejecutada en todos nodos")
            else:
                log_message("[Sin consenso] El nodo maestro no respondió OK, Error")
                
        else:
            log_message(f"[Error] La conexión con el nodo maestro no está activa.")
    except Exception as e:
        log_message(f"[Error] No se pudo enviar el mensaje al nodo maestro: {e}")
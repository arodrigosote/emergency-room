import sqlite3
from controllers.server_client import active_connections
from datetime import datetime
from utils.log import log_message
from controllers.server_client import get_client_socket_by_ip  # Asegúrate de tener una función para obtener el socket del cliente
from controllers.server_client import active_connections  # Asegúrate de tener un diccionario para mantener las conexiones activas

def enviar_consulta_sencilla(consulta):
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje = f"13|{hora_actual}|{consulta}"
    respuestas = []
    for destino, client_socket in active_connections.items():
        try:
            if client_socket.fileno() != -1:  # Verifica que el socket siga activo
                client_socket.send(mensaje.encode())
                log_message(f"[Mensaje enviado] A nodo {destino}: {mensaje}")
                
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
    try:
        if nodo_maestro.fileno() != -1:  # Verifica que el socket siga activo
            nodo_maestro.send(mensaje_completo.encode())
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
import sqlite3
from controllers.server_client import active_connections
from datetime import datetime
from utils.log import log_message


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
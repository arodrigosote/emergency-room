import os
from utils.log import log_message
from models.database import execute_query


def procesar_query(codigo_instruccion, mensaje, client_socket):
    try:
        _, hora_actual, query = mensaje.split("|")
        if codigo_instruccion == "10":  # Ejecutar consulta local
            resultado = execute_query(query)
            response = "OK" if resultado else "Error"
        elif codigo_instruccion == "11":  # Propagar consulta a otros nodos
            response = propagar_consulta_a_nodos(hora_actual, query, client_socket)
        client_socket.send(response.encode())
    except Exception as e:
        log_message(f"[Error] Al procesar la consulta: {e}")
        client_socket.send("Error".encode())

def propagar_consulta_a_nodos(hora_actual, query, active_connections):
    mensaje_nuevo = f"10|{hora_actual}|{query}"
    respuestas = []
    
    for destino, socket_cliente in active_connections.items():
        try:
            socket_cliente.send(mensaje_nuevo.encode())
            respuesta = socket_cliente.recv(1024).decode()
            respuestas.append(respuesta)
            log_message(f"[Nodo {destino}] Respuesta: {respuesta}")
        except Exception as e:
            log_message(f"[Error] Nodo {destino} no respondió: {e}")
    
    if all(r == "OK" for r in respuestas):
        log_message("[Consenso] Todos los nodos respondieron OK.")
        return "OK"
    log_message("[Sin consenso] No todos los nodos respondieron OK.")
    return "Error"

def guardar_cambios_base_datos(mensaje, client_socket):
    try:
        os.makedirs("database", exist_ok=True)
        archivo_path = os.path.join("database", "changestomake.txt")

        with open(archivo_path, "w") as archivo:
            for linea in mensaje.splitlines():
                if "#" in linea:
                    fecha_hora, consulta = linea.split("#", 1)
                    archivo.write(f"{fecha_hora.strip()}#{consulta.strip()}\n")
        
        log_message("[Info] Cambios guardados correctamente en 'changestomake.txt'.")
        client_socket.send("OK".encode())
    except Exception as e:
        log_message(f"[Error] No se pudo guardar los cambios: {e}")
        client_socket.send("Error".encode())

import sqlite3
from datetime import datetime
from utils.log import log_message
from controllers.server_client import get_client_socket_by_ip, active_connections  # Asegúrate de tener una función para obtener el socket del cliente
from controllers.nodes import get_network_nodes, get_own_node


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


def enviar_consulta_compleja(consulta):

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
            sala, cama = obtener_sala_y_cama()
            if sala and cama:
                # Reemplazar "00" con el valor de sala y "01" con el valor de cama
                consulta = consulta.replace("00", str(sala)).replace("01", str(cama))
                log_message("[Nodo] El nodo propio es el nodo maestro.")
                # Enviar mensaje a todos los nodos
                codigo = "10"
                enviar_mensaje_a_todos(codigo, consulta)
                log_message(f"[Nodo] Se asignó la cama {cama} en la sala {sala} al paciente.")
            else:
                log_message("[Nodo] No hay camas disponibles en ninguna sala.")
                print("No hay camas disponibles en ninguna sala.")
                
        else:
            log_message("[Nodo] El nodo propio no es el nodo maestro.")
            codigo = "11"
            enviar_mensaje_a_maestro_calculo_sala(master_node_ip, codigo, consulta)
    else:
        log_message("\n[Nodo Propio] No se encontró el nodo propio.")

def obtener_sala_y_cama():
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    
    # Obtener la sala con mayor disponibilidad relativa
    cursor.execute("""
        SELECT 
            salas_emergencia.id_sala 
        FROM 
            salas_emergencia
        LEFT JOIN 
            camas 
        ON 
            salas_emergencia.id_sala = camas.id_sala
        WHERE 
            salas_emergencia.estado = 'activado' 
            AND camas.estado = 'disponible'
        GROUP BY 
            salas_emergencia.id_sala
        ORDER BY 
            (CAST(COUNT(camas.id_cama) AS FLOAT) / salas_emergencia.capacidad_total) DESC
        LIMIT 1;
    """)
    sala = cursor.fetchone()
    
    if sala:
        # Obtener una cama disponible en la sala seleccionada
        cursor.execute("""
            SELECT id_cama 
            FROM camas 
            WHERE id_sala = ? AND estado = 'disponible' 
            LIMIT 1
        """, (sala[0],))
        cama = cursor.fetchone()
        
        if cama:
            print(f"Cama disponible: {cama[0]}")
            return sala[0], cama[0]
        else:
            print("No hay camas disponibles en esta sala.")
            return sala[0], None
    else:
        print("No hay salas activas con camas disponibles.")
        return None, None



def enviar_mensaje_a_todos(codigo_instruccion, mensaje):
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_completo = f"{codigo_instruccion}|{hora_actual}|{mensaje}"
    respuestas = []
    own_node = get_own_node()
    
    for destino, client_socket in active_connections.items():
        try:
            # Obtener la IP del nodo destino
            destino_ip = client_socket.getpeername()[0]
            
            # Verificar que el nodo destino no sea el nodo propio
            if destino_ip != own_node['ip']:
                if client_socket.fileno() != -1:  # Verifica que el socket siga activo
                    client_socket.send(mensaje_completo.encode())
                    log_message(f"[Mensaje enviado] A nodo {destino}: {mensaje_completo}")
                    
                    # Analizar la respuesta del servidor
                    respuesta = client_socket.recv(1024).decode()  # Tamaño del buffer ajustable
                    log_message(f"[Respuesta recibida] De nodo {destino}: {respuesta}")
                    respuestas.append(respuesta)
                else:
                    log_message(f"[Error] La conexión con el nodo {destino} no está activa.")
            else:
                log_message(f"[Nodo Propio] No se envía mensaje al nodo propio.")
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
        print(f"[Error] No se pudo enviar el mensaje al nodo maestro: {e}")
        print(f"[Debug] Detalles del error: {str(e)}")
        import traceback
        print(f"[Debug] Traceback: {traceback.format_exc()}")


def enviar_mensaje_a_maestro_calculo_sala(ip_nodo_maestro, codigo, mensaje):
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sala, cama = obtener_sala_y_cama()
    if sala and cama:
        # Reemplazar "00" con el valor de sala y "01" con el valor de cama
        mensaje = mensaje.replace("00", str(sala)).replace("01", str(cama))
    else:
        log_message("[Nodo] No hay camas disponibles en ninguna sala.")
        print("No hay camas disponibles en ninguna sala.")
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
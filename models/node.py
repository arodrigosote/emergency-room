import sqlite3
from datetime import datetime
from utils.log import log_message
from controllers.server_client import get_client_socket_by_ip, active_connections, elegir_nodo_maestro  # Asegúrate de tener una función para obtener el socket del cliente
from controllers.nodes import get_network_nodes, get_own_node
from models.database import guardar_cambios_db_changestomake
# from controllers.handle_down import verificar_conexiones


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
    own_node_ip = get_own_node()

    for destino_id, client_socket in active_connections.items():
        try:
            destino_ip = client_socket.getpeername()[0]

            if destino_ip != own_node_ip['ip']:
                # print(destino_ip)
                respuesta = enviar_mensaje(client_socket, codigo, mensaje)
                if respuesta:
                    respuestas.append(respuesta)
        except Exception as e:
            log_message(f"[Error] No se pudo enviar mensaje al nodo {destino_id}: {str(e)}")

    if codigo == "12":
        respuestas_texto = "\n".join(respuestas)
        return respuestas_texto
        
    if codigo == "14":
        return all(res == respuestas[0] for res in respuestas)

    consenso = True
    for res in respuestas:
        if res != "OK":
            consenso = False
            break

    if consenso:
        log_message("[Consenso] Todos los nodos respondieron OK.")
    else:
        log_message("[Sin consenso] No todos los nodos respondieron OK.")


def procesar_consulta(consulta, es_compleja=False):
    # verificar_conexiones()
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


def distribuir_carga(nodo_id):
    """Distribuye la carga de trabajo entre los nodos."""
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
                desconexion_en_todos = enviar_mensajes_a_todos("14", "", incluir_propio=False)
                if desconexion_en_todos:
                    calculo_distribucion(nodo_propio['ip'])

    except Exception as e:
        log_message(f"[Error] {str(e)}")
    pass

import sqlite3

def calculo_distribucion(ip_sala):
    """Reasigna las visitas de una sala inactiva a camas en salas activas, priorizando la disponibilidad."""
    try:
        with sqlite3.connect('nodos.db') as conn:
            cursor = conn.cursor()
            
            # Obtener las visitas vinculadas a la sala inactiva
            cursor.execute("""
                SELECT id_visita, id_cama, id_sala 
                FROM visitas_emergencia 
                WHERE id_sala = (SELECT id_sala FROM salas_emergencia WHERE ip = ?) AND estado = 'activa'
            """, (ip_sala,)) 
            visitas = cursor.fetchall()

            if not visitas:
                log_message(f"[Distribución] No se encontraron visitas activas para la sala con IP {ip_sala}.")
                return
            
            log_message(f"[Distribución] Se encontraron {len(visitas)} visitas activas en la sala con IP {ip_sala}.")
            
            # Verificar que la sala ya no está activa
            cursor.execute("""
                SELECT estado 
                FROM salas_emergencia 
                WHERE ip = ?
            """, (ip_sala,))
            sala_estado = cursor.fetchone()

            if not sala_estado or sala_estado[0] != 'inactiva':
                log_message(f"[Distribución] La sala con IP {ip_sala} no está marcada como inactiva.")
                return
            
            # Obtener salas activas con espacio disponible
            cursor.execute("""
                SELECT id_sala, ip, capacidad_disponible 
                FROM salas_emergencia 
                WHERE estado = 'activa' AND capacidad_disponible > 0
                ORDER BY capacidad_disponible DESC
            """)
            salas_activas = cursor.fetchall()

            if not salas_activas:
                log_message("[Distribución] No hay salas activas con camas disponibles.")
                return

            # Reasignar cada visita a la sala activa con más capacidad
            for visita in visitas:
                id_visita, id_cama, id_sala_origen = visita
                nueva_sala = None

                for sala in salas_activas:
                    id_nueva_sala, nueva_ip, capacidad_disponible = sala

                    # Buscar una cama disponible en la nueva sala
                    cursor.execute("""
                        SELECT id_cama 
                        FROM camas 
                        WHERE id_sala = ? AND estado = 'disponible'
                        LIMIT 1
                    """, (id_nueva_sala,))
                    nueva_cama = cursor.fetchone()

                    if nueva_cama:
                        nueva_sala = (id_nueva_sala, nueva_ip, nueva_cama[0])
                        break

                if not nueva_sala:
                    log_message(f"[Distribución] No se encontró una cama disponible para la visita {id_visita}.")
                    continue

                id_nueva_sala, nueva_ip, nueva_cama_id = nueva_sala

                # Actualizar la visita para asignarla a la nueva sala y cama
                cursor.execute("""
                    UPDATE visitas_emergencia 
                    SET nodo_ip = ?, id_sala = ?, id_cama = ? 
                    WHERE id_visita = ?
                """, (nueva_ip, id_nueva_sala, nueva_cama_id, id_visita))

                # Actualizar estado de la cama asignada
                cursor.execute("""
                    UPDATE camas 
                    SET estado = 'ocupada' 
                    WHERE id_cama = ?
                """, (nueva_cama_id,))

                # Liberar la cama anterior
                cursor.execute("""
                    UPDATE camas 
                    SET estado = 'disponible' 
                    WHERE id_cama = ?
                """, (id_cama,))

                # Actualizar capacidad disponible en las salas
                cursor.execute("""
                    UPDATE salas_emergencia 
                    SET capacidad_disponible = capacidad_disponible + 1 
                    WHERE id_sala = ?
                """, (id_sala_origen,))
                
                cursor.execute("""
                    UPDATE salas_emergencia 
                    SET capacidad_disponible = capacidad_disponible - 1 
                    WHERE id_sala = ?
                """, (id_nueva_sala,))

                conn.commit()
                log_message(f"[Distribución] Visita {id_visita} reasignada a sala {nueva_ip} y cama {nueva_cama_id}.")

    except Exception as e:
        log_message(f"[Error] {str(e)}")

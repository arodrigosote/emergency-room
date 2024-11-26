from controllers.server_client import active_connections, elegir_nodo_maestro, unactive_connections
from models.emergency_room import desactivar_sala
from controllers.nodes import get_network_nodes
from utils.log import log_message

def verificar_conexiones():
    """Verifica conexiones activas y recalcula el nodo maestro."""
    try:
        nodos_red = get_network_nodes()
        nodos_red_ips = {nodo['ip'] for nodo in nodos_red}
        nodos_activos = list(active_connections.keys())

        for nodo_id in nodos_activos:
            client_socket = active_connections.get(nodo_id)

            if client_socket is None or client_socket.fileno() == -1:
                nodo_ip = client_socket.getpeername()[0] if client_socket else "Desconocida"
                log_message(f"[Conexión perdida] Nodo {nodo_id} desconectado.")
                active_connections.pop(nodo_id, None)
                unactive_connections.append(nodo_id)

                desactivar_sala(nodo_ip)  # Desactivar recursos relacionados
                elegir_nodo_maestro()  # Recalcular nodo maestro

            else:
                destino_ip = client_socket.getpeername()[0]
                if destino_ip not in nodos_red_ips:
                    log_message(f"[Conexión perdida] Nodo {nodo_id} con IP {destino_ip} ya no está en la red.")
                    active_connections.pop(nodo_id, None)
                    elegir_nodo_maestro()
    except Exception as e:
        log_message(f"[Error] Verificación de conexiones: {e}")

from controllers.server_client import active_connections, elegir_nodo_maestro, unactive_connection
from models.emergency_room import desactivar_sala
from models.node import distribuir_carga
from controllers.nodes import get_network_nodes
from utils.log import log_message, log_database

def verificar_conexiones():
        """Verifica las conexiones activas y recalcula el nodo maestro si es necesario."""
        # print("Verificando conexiones...")
        try:
            nodos_red = get_network_nodes()
            nodos_activos = list(active_connections.keys())

            for nodo_id in nodos_activos:
                # print(f"Verificando nodo {nodo_id}...")
                client_socket = active_connections[nodo_id]
                destino_ip = client_socket.getpeername()[0]
                if destino_ip not in [nodo['ip'] for nodo in nodos_red]:
                    log_message(f"[Conexión perdida] Nodo {nodo_id} desconectado.")
                    print(f"[Conexión perdida] Nodo {nodo_id} desconectado.")
                    del active_connections[nodo_id]
                    unactive_connection = nodo_id
                    desactivar_sala(destino_ip)
                    elegir_nodo_maestro()
                    distribuir_carga(nodo_id)
                        
        except Exception as e:
            log_message(f"[Error] {str(e)}")


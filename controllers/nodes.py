from scapy.all import ARP, Ether, srp
import socket
from controllers.server_client import active_connections, elegir_nodo_maestro
from models.emergency_room import activar_sala, obtener_sala_y_cama, desactivar_sala

def get_own_node():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    # Obtener la dirección IP de la interfaz de red activa
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No se envía ningún dato, solo se utiliza para obtener la IP
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception as e:
        raise RuntimeError("No se pudo obtener la dirección IP de la interfaz de red") from e
    finally:
        s.close()

    return {
        'ip': local_ip,
        'mac': '00:00:00:00:00:00',  # Placeholder para la MAC del propio nodo
        'id': local_ip.split('.')[-1]
    }

def get_network_nodes():
    nodes = []
    own_node = get_own_node()

    # Incluir el propio nodo en la lista de nodos
    nodes.append(own_node)

    # Calcular el rango de la subred
    subnet = '.'.join(own_node['ip'].split('.')[:-1]) + '.0/24'

    # Crear el paquete ARP para el escaneo de la red
    paquete = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet)

    # Enviar el paquete y recibir respuestas
    resultado = srp(paquete, timeout=2, verbose=False)[0]

    for envio, respuesta in resultado:
        if respuesta.psrc != own_node['ip']:  # Excluir el propio nodo ya incluido
            nodes.append({
                'ip': respuesta.psrc, 
                'mac': respuesta.hwsrc,
                'id': respuesta.psrc.split('.')[-1]  # Agregar el ID como el último segmento de la IP
            })

    return nodes


def verificar_conexiones():
    """Verifica las conexiones activas y recalcula el nodo maestro si es necesario."""
    # print("Verificando conexiones...")
    try:
        nodos_red = get_network_nodes()
        nodos_activos = list(active_connections.keys())

        for nodo_id in nodos_activos:
            # print(f"Verificando nodo {nodo_id}...")
            client_socket = active_connections[nodo_id]
            if client_socket.fileno() == -1:  # Verifica que el socket siga activo
                nodo_ip = client_socket.getpeername()[0]
                print(f"[Conexión perdida] Nodo {nodo_id} desconectado.")
                log_message(f"[Conexión perdida] Nodo {nodo_id} desconectado.")
                del active_connections[nodo_id]
                unactive_connections.append(nodo_id)
                
                desactivar_sala(nodo_ip)

                # redistribuir_carga(nodo_ip)

                elegir_nodo_maestro()
            else:
                destino_ip = client_socket.getpeername()[0]
                if destino_ip not in [nodo['ip'] for nodo in nodos_red]:
                    log_message(f"[Conexión perdida] Nodo {nodo_id} desconectado.")
                    print(f"[Conexión perdida] Nodo {nodo_id} desconectado.")
                    del active_connections[nodo_id]
                    elegir_nodo_maestro()

    except Exception as e:
        log_message(f"[Error] {str(e)}")

from scapy.all import ARP, Ether, srp
import socket

def get_network_nodes():
    nodes = []
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

    # Calcular el rango de la subred
    subnet = '.'.join(local_ip.split('.')[:-1]) + '.0/24'

    # Crear el paquete ARP para el escaneo de la red
    paquete = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet)

    # Enviar el paquete y recibir respuestas
    resultado = srp(paquete, timeout=2, verbose=False)[0]

    for envio, respuesta in resultado:
        nodes.append({
            'ip': respuesta.psrc, 
            'mac': respuesta.hwsrc,
            'id': respuesta.psrc.split('.')[-1]  # Agregar el ID como el último segmento de la IP
        })

    return nodes


import os
import socket

def get_network_nodes():
    nodes = []
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    if local_ip.startswith("192."):
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

    subnet = '.'.join(local_ip.split('.')[:-1]) + '.'

    for i in range(1, 255):
        ip = subnet + str(i)
        response = os.system(f"ping -c 1 -w 1 {ip} > /dev/null 2>&1")
        if response == 0:
            nodes.append({'id': i, 'ip': ip})

    return nodes
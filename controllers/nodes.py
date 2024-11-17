import os
import netifaces

def get_network_nodes():
    nodes = []
    interfaces = netifaces.interfaces()
    local_ip = None

    for interface in interfaces:
        if netifaces.AF_INET in netifaces.ifaddresses(interface):
            addr_info = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]
            if addr_info['addr'] != '127.0.0.1':
                local_ip = addr_info['addr']
                break

    if local_ip is None:
        raise RuntimeError("No se pudo obtener la dirección IP de la interfaz de red")

    subnet = '.'.join(local_ip.split('.')[:-1]) + '.'

    for i in range(1, 255):
        ip = subnet + str(i)
        response = os.system(f"ping -c 1 -w 1 {ip} > /dev/null 2>&1")
        if response == 0:
            nodes.append({'id': i, 'ip': ip})

    return nodes
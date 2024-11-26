from scapy.all import ARP, Ether, srp
import socket


import socket
import fcntl
import struct
import os

def get_interface_ip(interface_name):
    """
    Obtiene la dirección IP de una interfaz específica.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', interface_name[:15].encode('utf-8'))
        )[20:24]
        return socket.inet_ntoa(ip)
    except OSError:
        raise RuntimeError(f"No se pudo obtener la IP para la interfaz: {interface_name}")

def get_interface_mac(interface_name):
    """
    Obtiene la dirección MAC de una interfaz específica.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mac = fcntl.ioctl(
            s.fileno(),
            0x8927,  # SIOCGIFHWADDR
            struct.pack('256s', interface_name[:15].encode('utf-8'))
        )[18:24]
        return ':'.join(f'{b:02x}' for b in mac)
    except OSError:
        raise RuntimeError(f"No se pudo obtener la MAC para la interfaz: {interface_name}")

def get_active_interface():
    """
    Detecta automáticamente la interfaz activa utilizada para la red.
    """
    # Se basa en obtener una interfaz activa conectándose a una dirección pública
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # Dirección pública conocida
        active_ip = s.getsockname()[0]
        active_interface = os.popen(f"ip -o -4 addr show | grep '{active_ip}'").read().split()[1]
        return active_interface
    except Exception as e:
        raise RuntimeError("No se pudo detectar la interfaz activa") from e
    finally:
        s.close()

def get_own_node():
    """
    Obtiene la dirección IP y MAC del nodo usando la interfaz activa.
    """
    try:
        interface_name = get_active_interface()  # Detecta la interfaz activa
        local_ip = get_interface_ip(interface_name)
        local_mac = get_interface_mac(interface_name)
        return {
            'ip': local_ip,
            'mac': local_mac,
            'id': local_ip.split('.')[-1]
        }
    except RuntimeError as e:
        raise RuntimeError(f"Error al obtener los datos del nodo: {e}")


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




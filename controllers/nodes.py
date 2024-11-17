import socket
import os

def get_network_nodes():
    nodes = []
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    subnet = '.'.join(local_ip.split('.')[:-1]) + '.'

    for i in range(1, 255):
        ip = subnet + str(i)
        response = os.system(f"ping -c 1 -w 1 {ip} > /dev/null 2>&1")
        if response == 0:
            nodes.append({'id': i, 'ip': ip})

    return nodes
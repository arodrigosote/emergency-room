import socket
import json

def conectar_a_servidor(host, conexiones_activas, port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Conectado a {host}:{port}")
        conexiones_activas.append((host, s))
        mensaje = {'id': 1, 'mensaje': 'Hola, servidor'}
        s.sendall(json.dumps(mensaje).encode('utf-8'))
        data = s.recv(1024)
        print(f"Recibido {data.decode('utf-8')} de {host}")

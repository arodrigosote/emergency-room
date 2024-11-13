import socket
import json

def send_message(conexion, mensaje):
    mensaje_dict = {'id': 2, 'mensaje': mensaje}
    conexion.sendall(json.dumps(mensaje_dict).encode('utf-8'))
    data = conexion.recv(1024)
    print(f"Respuesta recibida: {data.decode('utf-8')}")
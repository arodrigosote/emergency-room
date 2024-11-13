import socket
import threading
import json

def iniciar_servidor(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print(f"Servidor iniciado en {host}:{port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=manejar_conexion, args=(conn, addr)).start()

def manejar_conexion(conn, addr):
    print(f"Conexión establecida con {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            mensaje = json.loads(data.decode('utf-8'))
            manejar_mensaje(mensaje)
            conn.sendall(data)
    print(f"Conexión cerrada con {addr}")

def manejar_mensaje(mensaje):
    identificador = mensaje.get('id')
    contenido = mensaje.get('mensaje')
    print(f"Mensaje recibido - ID: {identificador}, Contenido: {contenido}")
    # Aquí se pueden agregar más instrucciones basadas en el identificador

import socket
import threading
from models.messages import add_received_message, add_sent_message
from models.devices import add_connected_device, remove_connected_device
from controllers.utils import get_current_timestamp

PORT = 12345
HOST = '0.0.0.0'

def handle_client(conn, addr):
    print(f"\n{get_current_timestamp()} - Dispositivo conectado desde {addr}")
    add_connected_device(addr)

    try:
        while True:
            message = conn.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"{get_current_timestamp()} - Mensaje recibido de {addr}: {message}")
            add_received_message(addr[0], message)

            response_message = f"Mensaje recibido de {addr[0]}"
            response = f"\n{get_current_timestamp()} - Respuesta a {addr}: {response_message}"
            conn.send(response.encode('utf-8'))
            add_sent_message(addr[0], response_message)
            add_received_message(addr[0], response_message)
    except:
        pass
    finally:
        remove_connected_device(addr)
        conn.close()
        print(f"\n{get_current_timestamp()} - Dispositivo desconectado {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Escuchando en el puerto {PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()
import socket
from models.messages import add_sent_message
from models.devices import client_sockets
from controllers.utils import get_current_timestamp, print_connected_devices

PORT = 12345

def start_client(target_ip):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((target_ip, PORT))
    print(f"\n{get_current_timestamp()} - Conectado al servidor {target_ip}")
    client_sockets[target_ip] = client

def send_message_to_device(device_ip, message):
    timestamp = get_current_timestamp()
    full_message = f"{timestamp} - {message}"
    client_sockets[device_ip].send(full_message.encode('utf-8'))
    add_sent_message(device_ip, full_message)

    response = client_sockets[device_ip].recv(1024).decode('utf-8')
    print(f"\n{timestamp} - Respuesta del servidor: {response}")

def send_message_to_all_devices(message):
    timestamp = get_current_timestamp()
    full_message = f"{timestamp} - {message}"
    for device_ip, client_socket in client_sockets.items():
        client_socket.send(full_message.encode('utf-8'))
        add_sent_message(device_ip, full_message)

        response = client_socket.recv(1024).decode('utf-8')
        print(f"\n{timestamp} - Respuesta del servidor {device_ip}: {response}")
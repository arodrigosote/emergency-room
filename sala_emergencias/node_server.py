
import socket
import threading

def handle_client_connection(client_socket):
    request = client_socket.recv(1024)
    print(f"Recibido: {request.decode('utf-8')}")
    client_socket.send("CONFIRMADO".encode('utf-8'))
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8080))
    server.listen(5)
    print("Servidor escuchando en el puerto 8080")

    while True:
        client_sock, address = server.accept()
        print(f"Conexión aceptada de {address}")
        client_handler = threading.Thread(target=handle_client_connection, args=(client_sock,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
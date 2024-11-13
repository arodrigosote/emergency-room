import socket

class Messaging:
    def __init__(self, ip, port=8080):
        self.ip = ip
        self.port = port

    def send_message(self, connection, message):
        try:
            connection.send(message.encode('utf-8'))
            response = connection.recv(1024).decode('utf-8')
            return response
        except ConnectionError:
            print("Error al enviar el mensaje")
            return None

    def start_server(self, handle_message):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen(5)
        print(f"Servidor escuchando en {self.ip}:{self.port}")

        while True:
            client_sock, address = server.accept()
            print(f"Conexión aceptada de {address}")
            message = client_sock.recv(1024).decode('utf-8')
            response = handle_message(message, address)
            client_sock.send(response.encode('utf-8'))
            client_sock.close()

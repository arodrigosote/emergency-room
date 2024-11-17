import socket
import threading
from controllers.nodes import get_network_nodes
from utils.menu import mostrar_menu

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            response = f"Comando recibido: {data.decode()}"
            client_socket.send(response.encode())
    except Exception as e:
        print(f"Error con el cliente: {e}")
    finally:
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(("localhost", 8080))
        server.listen(15)
        print("\nServidor escuchando en el puerto 8080")
        while True:
            client_socket, addr = server.accept()
            print(f"Conexión aceptada de {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
    finally:
        server.close()

def connect_clients(nodes):
    for node in nodes:
        node_id = int(node['id'])
        if node_id in [1, 2, 254]:
            print(f"Saltando conexión para el nodo con ID {node_id}")
            continue
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((node['ip'], 8080))
            response = client.recv(4096)
            print(f"Respuesta del servidor {node['ip']}: {response.decode()}")
        except Exception as e:
            print(f"No se pudo conectar con el nodo {node['ip']}: {e}")
        finally:
            client.close()

def opcion1():
    nodes = get_network_nodes()
    print("Nodos en la red:")
    for node in nodes:
        print(f"ID: {node['id']}, IP: {node['ip']}, MAC: {node['mac']}")
    
    connect_clients(nodes)

def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        if opcion == '1':
            opcion1()
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida, intente de nuevo.")

if __name__ == "__main__":
    main()

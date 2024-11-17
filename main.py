from controllers.nodes import get_network_nodes
from utils.menu import mostrar_menu
import threading
import socket

def handle_client(client_socket):
    # Manejar la conexión con el cliente
    client_socket.send(b"Conexion establecida con el servidor")
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(15)
    print("Servidor escuchando en el puerto 9999")

    while True:
        client_socket, addr = server.accept()
        print(f"Conexión aceptada de {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def connect_clients(nodes):
    for node in nodes:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((node['ip'], 9999))
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
    

    

def opcion2(nodes):
    print("Opción 3 seleccionada")

def opcion3():
    print("Opción 3 seleccionada")

def opcion4():
    print("Opción 4 seleccionada")



def main():
    # Iniciar el servidor en un hilo separado
    server_thread = threading.Thread(target=start_server)
    server_thread.start()


    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        if opcion == '1':
            opcion1()
        elif opcion == '2':
            opcion2()
        elif opcion == '3':
            opcion3()
        elif opcion == '4':
            opcion4()
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida, intente de nuevo.")

if __name__ == "__main__":
    main()



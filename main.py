import socket
import threading
from controllers.nodes import get_network_nodes
from utils.menu import mostrar_menu

# Diccionario para mantener las conexiones activas
active_connections = {}

def handle_client(client_socket, addr):
    try:
        print(f"[Servidor] Conexión establecida con {addr}")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"[Mensaje recibido] De {addr}: {data.decode()}")
            response = f"Servidor recibió: {data.decode()}"
            client_socket.send(response.encode())
    except Exception as e:
        print(f"Error con el cliente {addr}: {e}")
    finally:
        client_socket.close()
        print(f"[Servidor] Conexión cerrada con {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permitir reutilizar el puerto en caso de que esté en TIME_WAIT
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", 9999))
        server.listen(15)
        print("\n[Servidor] Escuchando en el puerto 9999")
        while True:
            client_socket, addr = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_handler.start()
    except OSError as e:
        if "Address already in use" in str(e):
            print("[Error] El puerto 9999 ya está en uso. Liberando...")
            server.close()
            # Intentar reiniciar el servidor
            start_server()
        else:
            print(f"[Error] Ocurrió un problema: {e}")
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
    finally:
        server.close()

def connect_clients(nodes):
    for node in nodes:
        node_id = int(node['id'])
        if node_id in [1, 2, 254]:  # Salta nodos específicos (opcional)
            print(f"Saltando conexión para el nodo con ID {node_id}")
            continue

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((node['ip'], 9999))
            active_connections[node['id']] = client  # Almacena la conexión activa
            print(f"[Conexión exitosa] Nodo {node['id']} conectado.")
        except Exception as e:
            print(f"[Error] No se pudo conectar con el nodo {node['ip']}: {e}")
        finally:
            if node['id'] not in active_connections:
                client.close()

def enviar_mensaje():
    print("[Enviar mensaje] Nodos disponibles:")
    for node_id in active_connections.keys():
        print(f"ID: {node_id}")
    destino = input("Ingrese el ID del nodo destino: ")
    mensaje = input("Escriba el mensaje a enviar: ")

    try:
        destino = int(destino)
        if destino in active_connections:
            active_connections[destino].send(mensaje.encode())
            print(f"[Mensaje enviado] A nodo {destino}: {mensaje}")
        else:
            print(f"[Error] Nodo {destino} no está conectado.")
    except Exception as e:
        print(f"[Error] No se pudo enviar el mensaje: {e}")

def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    while True:
        nodes = get_network_nodes()
        print("[Nodos en la red]:")
        for node in nodes:
            print(f"ID: {node['id']}, IP: {node['ip']}, MAC: {node['mac']}")
        connect_clients(nodes)
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        if opcion == '1':
            print("[Escaneo de red] Buscando nodos disponibles...")
        elif opcion == '2':
            enviar_mensaje()
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida, intente de nuevo.")

if __name__ == "__main__":
    main()

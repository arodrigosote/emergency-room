import socket
import threading

# Diccionario para mantener las conexiones activas
active_connections = {}

def handle_client(client_socket, addr):
    # Maneja la conexión con un cliente
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            mensaje = data.decode()
            if mensaje == "CHECK_CONNECTION":
                # Verificar si estamos conectados de vuelta
                if addr[0] not in active_connections:
                    client_socket.send("NOT_CONNECTED".encode())
                else:
                    client_socket.send("CONNECTED".encode())
            else:
                print(f"[Mensaje recibido] De {addr}: {mensaje}")
                response = f"Servidor recibió: {mensaje}"
                client_socket.send(response.encode())
    except Exception as e:
        print('')
    finally:
        client_socket.close()

def start_server():
    # Inicia el servidor y maneja solicitudes de clientes
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", 9999))
        server.listen(15)
        print("\n[Servidor] Escuchando en el puerto 9999")
        while True:
            client_socket, addr = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
            client_handler.start()
    except OSError as e:
        if "Address already in use" in str(e):
            print("[Error] El puerto 9999 ya está en uso. Liberando...")
            server.close()
            # Liberar conexiones activas
            for conn in active_connections.values():
                conn.close()
            active_connections.clear()
            start_server()  # Intentar reiniciar el servidor
        else:
            print(f"[Error] Problema al iniciar el servidor: {e}")
    except Exception as e:
        print(f"[Error] Error desconocido al iniciar el servidor: {e}")
    finally:
        server.close()

def connect_clients(nodes):
    # Conecta con los nodos de la red
    for node in nodes:
        node_id = int(node['id'])
        if node_id in [1, 2, 254]:  # Opcional: omitir nodos específicos
            continue

        if node_id in active_connections:
            print(f"[Info] Nodo {node_id} ya está conectado.")
            continue

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"[Intentando conectar] Nodo ID: {node_id}, IP: {node['ip']}")
            client.connect((node['ip'], 9999))
            active_connections[node_id] = client  # Almacena la conexión activa
            print(f"[Conexión exitosa] Nodo {node_id} conectado. Activas: {list(active_connections.keys())}")

            # Verificar si el nodo remoto está conectado de vuelta
            client.send("CHECK_CONNECTION".encode())
            respuesta = client.recv(1024).decode()
            if respuesta == "NOT_CONNECTED":
                print(f"[Conexión inversa] Nodo {node_id} no está conectado de vuelta. Intentando conectar...")
                connect_back(node['ip'], node_id)
        except Exception as e:
            print(f"[Error] No se pudo conectar con el nodo {node['ip']}: {e}")
        finally:
            if node_id not in active_connections:
                client.close()  # Asegurarse de cerrar conexiones fallidas

def connect_back(ip, node_id):
    # Conecta de vuelta al nodo que no está conectado
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"[Intentando conectar de vuelta] Nodo ID: {node_id}, IP: {ip}")
        client.connect((ip, 9999))
        active_connections[node_id] = client  # Almacena la conexión activa
        print(f"[Conexión inversa exitosa] Nodo {node_id} conectado de vuelta. Activas: {list(active_connections.keys())}")
    except Exception as e:
        print(f"[Error] No se pudo conectar de vuelta con el nodo {ip}: {e}")
    finally:
        if node_id not in active_connections:
            client.close()  # Asegurarse de cerrar conexiones fallidas

def enviar_mensaje():
    # Envia un mensaje a un nodo
    print("[Enviar mensaje] Nodos disponibles:")
    for node_id in active_connections.keys():
        print(f"ID: {node_id}")
    destino = input("Ingrese el ID del nodo destino: ")
    mensaje = input("Escriba el mensaje a enviar: ")

    try:
        destino = int(destino)
        if destino in active_connections:
            client_socket = active_connections[destino]
            if client_socket.fileno() != -1:  # Verifica que el socket siga activo
                client_socket.send(mensaje.encode())
                print(f"[Mensaje enviado] A nodo {destino}: {mensaje}")
            else:
                print(f"[Error] La conexión con el nodo {destino} no está activa.")
        else:
            print(f"[Error] Nodo {destino} no está conectado.")
    except Exception as e:
        print(f"[Error] No se pudo enviar el mensaje: {e}")

def mostrar_conexiones():
    # Muestra las conexiones activas
    print("[Conexiones activas]:")
    for node_id in active_connections.keys():
        print(f"ID: {node_id}")
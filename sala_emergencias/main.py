import socket
import threading
from middleware.master_election import MasterElection
from controllers.master_node import MasterNode
from middleware.messaging import Messaging

# Lista de direcciones IP de los nodos
NODE_IPS = ["192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4"]

def get_node_id_from_ip(ip):
    return int(ip.split('.')[-1])

def connect_to_nodes():
    connections = []
    active_node_ids = []
    for ip in NODE_IPS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, 8080))  # Asumiendo que los nodos escuchan en el puerto 8080
            s.send("CONECTAR".encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            if response == "CONFIRMADO":
                connections.append(s)
                active_node_ids.append(get_node_id_from_ip(ip))
                print(f"Conectado al nodo {ip} y confirmado")
            else:
                print(f"Conexión al nodo {ip} no confirmada")
        except ConnectionError:
            print(f"No se pudo conectar al nodo {ip}")
    return connections, active_node_ids

def handle_message(message, address):
    print(f"Recibido: {message} de {address}")
    return "CONFIRMADO"

def main_menu():
    print("Sistema de Gestión de Emergencias Médicas")
    print("1. Registrar visita de emergencia")
    print("2. Consultar lista de pacientes")
    print("3. Consultar lista de doctores")
    print("4. Consultar lista de trabajadores sociales")
    print("5. Actualizar lista de pacientes")
    print("6. Actualizar lista de doctores")
    print("7. Actualizar lista de trabajadores sociales")
    print("8. Cerrar visita de emergencia")
    print("9. Salir")

    choice = input("Seleccione una opción: ")
    return choice

def main():
    local_ip = socket.gethostbyname(socket.gethostname())
    messaging = Messaging(local_ip)

    # Iniciar el servidor en un hilo separado
    server_thread = threading.Thread(target=messaging.start_server, args=(handle_message,))
    server_thread.daemon = True
    server_thread.start()

    connections, active_node_ids = connect_to_nodes()
    node_id = get_node_id_from_ip(local_ip)  # Obtener el ID del nodo desde la IP local
    
    election = MasterElection(node_id, [id for id in active_node_ids if id != node_id])  # IDs de los otros nodos
    election.start()
    election.start_election()

    if election.is_master():
        master_node = MasterNode()
        print("Este nodo es el maestro.")
    else:
        print("Este nodo no es el maestro.")

    while True:
        choice = main_menu()
        if choice == '1':
            # lógica para registrar visita de emergencia
            pass
        elif choice == '2':
            # lógica para consultar lista de pacientes
            pass
        elif choice == '3':
            # lógica para consultar lista de doctores
            pass
        elif choice == '4':
            # lógica para consultar lista de trabajadores sociales
            pass
        elif choice == '5':
            # lógica para actualizar lista de pacientes
            pass
        elif choice == '6':
            # lógica para actualizar lista de doctores
            pass
        elif choice == '7':
            # lógica para actualizar lista de trabajadores sociales
            pass
        elif choice == '8':
            # lógica para cerrar visita de emergencia
            pass
        elif choice == '9':
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida, por favor intente de nuevo.")

if __name__ == "__main__":
    main()

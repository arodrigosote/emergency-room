import socket
from middleware.master_election import MasterElection
from controllers.master_node import MasterNode

# Lista de direcciones IP de los nodos
NODE_IPS = ["192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4"]

def connect_to_nodes():
    connections = []
    for ip in NODE_IPS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, 8080))  # Asumiendo que los nodos escuchan en el puerto 8080
            connections.append(s)
            print(f"Conectado al nodo {ip}")
        except ConnectionError:
            print(f"No se pudo conectar al nodo {ip}")
    return connections

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
    connections = connect_to_nodes()
    node_id = 1  # Asignar un ID único a este nodo
    election = MasterElection(node_id, [2, 3, 4])  # IDs de los otros nodos
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

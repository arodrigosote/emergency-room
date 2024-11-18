import socket
import threading
from controllers.nodes import get_network_nodes
from utils.menu import mostrar_menu
from controllers.server_client import start_server, connect_clients, enviar_mensaje, mostrar_conexiones
from controllers.messages import enviar_mensaje_a_nodo, enviar_mensaje_a_todos

# Diccionario para mantener las conexiones activas
active_connections = {}

def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    try:
        while True:
            nodes = get_network_nodes()  # Obtener nodos de la red
            for node in nodes:
                node_id = node.get("id")  
                if node_id not in active_connections:
                    conn = connect_clients([node])
                    if conn:
                        active_connections[node_id] = conn

            mostrar_menu()

            try:
                opcion = input("Seleccione una opción: ")
            except EOFError:
                print("Entrada interrumpida. Saliendo...")
                break

            if opcion == '1':
                print("[Escaneo de red] Buscando nodos disponibles...")
            elif opcion == '2':
                nodo_id = input("Ingrese el ID del nodo al que desea enviar el mensaje: ")
                mensaje = input("Ingrese el mensaje a enviar: ")
                enviar_mensaje_a_nodo(mensaje, nodo_id)
            elif opcion == '3':
                mensaje = input("Ingrese el mensaje a enviara todos: ")
                enviar_mensaje_a_todos()
            elif opcion == '5':
                print("Saliendo...")
                break
            else:
                print("Opción no válida, intente de nuevo.")
    finally:
        # Liberar recursos al salir
        for conn in active_connections.values():
            if hasattr(conn, 'close'):
                conn.close()
        active_connections.clear()

if __name__ == "__main__":
    main()

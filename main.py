import socket
import threading
from controllers.nodes import get_network_nodes
from utils.menu import mostrar_menu
from controllers.server_client import start_server, connect_clients, enviar_mensaje, mostrar_conexiones

# Diccionario para mantener las conexiones activas
active_connections = {}

def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    try:
        while True:
            nodes = get_network_nodes()  # Obtener nodos de la red
            for node in nodes:
                if node not in active_connections:
                    conn = connect_clients([node])  # Establecer conexión
                    if conn:  # Si la conexión fue exitosa
                        active_connections[node] = conn

            mostrar_menu()
            try:
                opcion = input("Seleccione una opción: ")
            except EOFError:
                print("Entrada interrumpida. Saliendo...")
                break

            if opcion == '1':
                print("[Escaneo de red] Buscando nodos disponibles...")
            elif opcion == '2':
                enviar_mensaje()
            elif opcion == '3':
                mostrar_conexiones()
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

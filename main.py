import socket
import threading
from controllers.nodes import get_network_nodes
from utils.menu import mostrar_menu, mostrar_menu_trabajador_social, mostrar_menu_doctor, realizar_accion_trabajador_social, realizar_accion_doctor, mostrar_menu_utilidades, realizar_accion_utilidades, mostrar_menu_utilidades
from utils.log import log_message
from controllers.server_client import start_server, connect_clients, mostrar_conexiones
from controllers.messages import enviar_mensaje_a_nodo, enviar_mensaje_a_todos
from controllers.database import init_db, agregar_doctores, agregar_salas_emergencia
from models.emergency_room import agregar_sala_emergencia, listar_salas_emergencia
import os

# Diccionario para mantener las conexiones activas
active_connections = {}

def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    init_db()

    # Ruta completa del archivo a limpiar
    history_dir = os.path.join(os.path.dirname(__file__), 'history')
    db_changes_file = os.path.join(history_dir, 'db_changes.txt')
    server_log_file = os.path.join(history_dir, 'server_log.txt')

    # Verificar si el archivo existe y limpiarlo
    if os.path.exists(db_changes_file):
        open(db_changes_file, 'w').close()
        log_message(f"\n[Archivo] El archivo 'db_changes.txt' ha sido limpiado.")
    else:
        log_message(f"\n[Advertencia] El archivo 'db_changes.txt' no existe.")
    
        # Verificar si el archivo existe y limpiarlo
    if os.path.exists(server_log_file):
        open(server_log_file, 'w').close()
        log_message(f"\n[Archivo] El archivo 'db_changes.txt' ha sido limpiado.")
    else:
        log_message(f"\n[Advertencia] El archivo 'db_changes.txt' no existe.")

    # Agregar una nueva sala de emergencia
    agregar_salas_emergencia()
    agregar_doctores()

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
                mostrar_menu_trabajador_social()
                opcion_ts = input("Seleccione una opción: ")
                realizar_accion_trabajador_social(opcion_ts)
            elif opcion == '2':
                mostrar_menu_doctor()
                opcion_doc = input("Seleccione una opción: ")
                realizar_accion_doctor(opcion_doc)
            elif opcion == '3':
                mostrar_menu_utilidades()
                opcion_util = input("Seleccione una opción: ")
                realizar_accion_utilidades(opcion_util)
            elif opcion == '4':
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

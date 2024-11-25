import socket
import threading
from controllers.nodes import get_network_nodes, get_own_node
from utils.menu import mostrar_menu, mostrar_menu_trabajador_social, mostrar_menu_doctor, realizar_accion_trabajador_social, realizar_accion_doctor, mostrar_menu_utilidades, realizar_accion_utilidades, mostrar_menu_utilidades, mostrar_menu_tablas, realizar_accion_tablas
from utils.log import log_message
from controllers.server_client import start_server, connect_to_node, mostrar_conexiones, active_connections, elegir_nodo_maestro
from controllers.messages import enviar_mensaje_a_nodo, enviar_mensaje_a_todos
from controllers.database import init_db, agregar_salas_emergencia, ejecutar_dbchanges
from models.emergency_room import activar_sala
from models.camas import agregar_camas
from models.trabajadores import listar_trabajadores_sociales, agregar_trabajadores_sociales
from models.doctors import agregar_doctores, listar_doctores_ocupados
import os

# Diccionario para mantener las conexiones activas

def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    init_db()

    # Ruta completa del archivo a limpiar
    history_dir = os.path.join(os.path.dirname(__file__), 'history')
    database_dir = os.path.join(os.path.dirname(__file__), 'database')
    db_changes_file = os.path.join(history_dir, 'db_changes.txt')
    server_log_file = os.path.join(history_dir, 'server_log.txt')
    dbchangestomake_file = os.path.join(database_dir, 'changestomake.txt')

    # Verificar si el archivo existe y limpiarlo
    if os.path.exists(db_changes_file):
        open(db_changes_file, 'w').close()
        log_message(f"[Archivo] El archivo 'db_changes.txt' ha sido limpiado.")
    else:
        log_message(f"[Advertencia] El archivo 'db_changes.txt' no existe.")
    
        # Verificar si el archivo existe y limpiarlo
    if os.path.exists(server_log_file):
        open(server_log_file, 'w').close()
        log_message(f"[Archivo] El archivo 'server_log.txt' ha sido limpiado.")
    else:
        log_message(f"[Advertencia] El archivo 'server_log.txt' no existe.")
    
    if os.path.exists(dbchangestomake_file):
        open(dbchangestomake_file, 'w').close()
        log_message(f"[Archivo] El archivo 'changestomake.txt' ha sido limpiado.")
    else:
        log_message(f"[Advertencia] El archivo 'changestomake.txt' no existe.")

    # Agregar una nueva sala de emergencia
    agregar_salas_emergencia()
    agregar_doctores()
    agregar_camas()
    agregar_trabajadores_sociales()

    nodes = get_network_nodes()  # Obtener nodos de la red

    for node in nodes:
        node_id = node.get("id")  
        if node_id not in active_connections:
            conn = connect_to_node([node])
            if conn:
                active_connections[node_id] = conn
    

    own_node = get_own_node()
    
    activar_sala(own_node['ip'])

    ejecutar_dbchanges()

    try:
        while True:
            
            mostrar_menu()

            try:
                opcion = input("Seleccione una opción: ")
            except EOFError:
                print("Entrada interrumpida. Saliendo...")
                break

            if opcion == '1':
                listar_trabajadores_sociales()
                id_trabajador = input("¿Quién realizará acciones? (Ingrese el ID del trabajador social): ")
                mostrar_menu_trabajador_social()
                opcion_ts = input("Seleccione una opción: ")
                realizar_accion_trabajador_social(id_trabajador,opcion_ts)
            elif opcion == '2':
                listar_doctores_ocupados()
                id_doctor = input("¿Quíen realiza la opción? (Ingrese el ID del doctor): ")
                mostrar_menu_doctor()
                opcion_doc = input("Seleccione una opción: ")
                realizar_accion_doctor(id_doctor, opcion_doc)
            elif opcion == '3':
                mostrar_menu_utilidades()
                opcion_util = input("Seleccione una opción: ")
                realizar_accion_utilidades(opcion_util)
            elif opcion == '4':
                mostrar_menu_tablas()
                opcion_tablas = input("Seleccione una opción: ")
                realizar_accion_tablas(opcion_tablas)
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

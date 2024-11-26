import socket
import threading
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from controllers.nodes import get_network_nodes, get_own_node
from utils.menu import (
    mostrar_menu, mostrar_menu_trabajador_social, mostrar_menu_doctor,
    realizar_accion_trabajador_social, realizar_accion_doctor,
    mostrar_menu_utilidades, realizar_accion_utilidades,
    mostrar_menu_tablas, realizar_accion_tablas,
    mostrar_menu_admin, realizar_accion_admin
)
from utils.log import log_message
from controllers.server_client import start_server, connect_to_node, active_connections
from controllers.database import init_db, agregar_salas_emergencia, ejecutar_dbchanges
from controllers.handle_down import verificar_conexiones
from models.emergency_room import activar_sala
from models.camas import agregar_camas
from models.trabajadores import listar_trabajadores_sociales, agregar_trabajadores_sociales
from models.doctors import agregar_doctores, listar_doctores_ocupados
from models.node import solicitar_cambios_db

stop_event = threading.Event()  # Evento para manejar la terminación del programa


def verificar_conexiones_en_hilo():
    """Ejecuta la verificación de conexiones activas continuamente."""
    while not stop_event.is_set():
        verificar_conexiones()
        threading.Event().wait(1)  # Intervalo de 1 segundo


def conectar_nodo(node):
    """Conecta un nodo a la red."""
    node_id = node.get("id")
    if node_id not in active_connections:
        conn = connect_to_node(node)
        if conn:
            active_connections[node_id] = conn


def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    init_db()

    # Limpieza de archivos históricos
    history_dir = os.path.join(os.path.dirname(__file__), 'history')
    database_dir = os.path.join(os.path.dirname(__file__), 'database')
    files_to_clean = [
        (os.path.join(history_dir, 'db_changes.txt'), 'db_changes.txt'),
        (os.path.join(history_dir, 'server_log.txt'), 'server_log.txt'),
        (os.path.join(database_dir, 'changestomake.txt'), 'changestomake.txt'),
    ]

    for file_path, file_name in files_to_clean:
        if os.path.exists(file_path):
            open(file_path, 'w').close()
            log_message(f"[Archivo] El archivo '{file_name}' ha sido limpiado.")
        else:
            log_message(f"[Advertencia] El archivo '{file_name}' no existe.")

    # Configuración inicial de la base de datos
    agregar_salas_emergencia()
    agregar_doctores()
    agregar_camas()
    agregar_trabajadores_sociales()

    # Conectar a nodos
    print("Conectando a la red...")
    nodes = get_network_nodes()
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(conectar_nodo, nodes)
    print("Conexiones establecidas.")

    # Activar sala propia
    own_node = get_own_node()
    activar_sala(own_node['ip'])

    # Sincronización inicial de base de datos
    solicitar_cambios_db()
    ejecutar_dbchanges()

    print("\n\n---------------------------------------------------")
    print("|                                                 |")
    print("| Bienvenido al sistema de gestión de emergencias |")
    print("|              Fabian Armenta                     |")
    print("|              Tania Gomez                        |")
    print("|              Nayeli Sierra                      |")
    print("|              Rodrigo Sotelo                     |")
    print("|                                                 |")
    print("---------------------------------------------------")

    try:
        # Crear y empezar el hilo para verificar conexiones
        verificar_conexiones_thread = threading.Thread(target=verificar_conexiones_en_hilo, daemon=True)
        verificar_conexiones_thread.start()

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
                realizar_accion_trabajador_social(id_trabajador, opcion_ts)
            elif opcion == '2':
                listar_doctores_ocupados()
                id_doctor = input("¿Quién realiza la opción? (Ingrese el ID del doctor): ")
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
                mostrar_menu_admin()
                opcion_admin = input("Seleccione una opción: ")
                realizar_accion_admin(opcion_admin)
            elif opcion == '6':
                print("Saliendo...")
                break
            else:
                print("Opción no válida, intente de nuevo.")
    finally:
        # Liberar recursos al salir
        stop_event.set()  # Detener hilos de largo plazo
        if 'verificar_conexiones_thread' in locals():
            verificar_conexiones_thread.join()
        for conn in active_connections.values():
            if hasattr(conn, 'close'):
                conn.close()
        active_connections.clear()


if __name__ == "__main__":
    main()

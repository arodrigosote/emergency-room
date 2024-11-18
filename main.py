import socket
import threading
from controllers.nodes import get_network_nodes
from utils.menu import mostrar_menu, mostrar_menu_trabajador_social, mostrar_menu_doctor
from controllers.server_client import start_server, connect_clients, enviar_mensaje, mostrar_conexiones, elegir_nodo_maestro
from controllers.messages import enviar_mensaje_a_nodo, enviar_mensaje_a_todos, enviar_mensaje_consenso, procesar_respuesta_consenso
from controllers.database import init_db, agregar_sala_emergencia  # Importar las funciones para inicializar la base de datos y agregar sala de emergencia

# Diccionario para mantener las conexiones activas
active_connections = {}

def main():
    # Inicializar la base de datos
    init_db()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Agregar una nueva sala de emergencia
    #agregar_sala_emergencia("Sala Principal", 5)

    try:
        while True:
            nodes = get_network_nodes()  # Obtener nodos de la red
            for node in nodes:
                node_id = node.get("id")  
                if node_id not in active_connections:
                    conn = connect_clients([node])
                    if conn:
                        active_connections[node_id] = conn

            master_node = elegir_nodo_maestro(nodes)  # Elegir el nodo maestro

            mostrar_menu()

            try:
                opcion = input("Seleccione una opción: ")
            except EOFError:
                print("Entrada interrumpida. Saliendo...")
                break

            if opcion == '1':
                # Enviar mensaje de consenso antes de registrar visita
                respuestas = enviar_mensaje_consenso("CONSENSO: Registrar visita de emergencia")
                if procesar_respuesta_consenso(respuestas):
                    print("Registrando visita de emergencia...")
                else:
                    print("No se pudo registrar la visita de emergencia por falta de consenso.")
            elif opcion == '2':
                # Enviar mensaje de consenso antes de cerrar visita
                respuestas = enviar_mensaje_consenso("CONSENSO: Cerrar visita de emergencia")
                if procesar_respuesta_consenso(respuestas):
                    print("Cerrando visita de emergencia...")
                else:
                    print("No se pudo cerrar la visita de emergencia por falta de consenso.")
            elif opcion == '3':
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

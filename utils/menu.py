import threading
from models.emergency_room import listar_salas_emergencia
from models.doctors import listar_doctores, agregar_doctor, actualizar_doctor
from models.camas import listar_camas
from models.pacientes import listar_pacientes, agregar_paciente, actualizar_paciente
from models.visitas import listar_visitas, agregar_visita, cerrar_visita_emergencia
from models.master_node import obtener_nodo_maestro
from models.trabajadores import listar_trabajadores_sociales, agregar_trabajador, actualizar_trabajador
from controllers.database import mostrar_log_base_datos, mostrar_log_servidor, mostrar_log_changestomake
from utils.log import log_message
from controllers.nodes import get_network_nodes
from controllers.server_client import active_connections



def mostrar_menu():
    print("\n\nMenú:")
    print("1. Trabajador Social")
    print("2. Doctor")
    print("3. Utilidades")
    print("4. Tablas")
    print("5. Admin")
    print("6. Salir")


# Funciones para mostrar y realizar acciones en los menús
def mostrar_menu_trabajador_social():
    print("\nMenú Trabajador Social:")
    print("1. Registrar visita emergencia")
    print("5. Volver")

def realizar_accion_trabajador_social(id_trabajador,opcion):
    
    if opcion == '1':
        print("\nRegistrar visita emergencia")
        agregar_visita(id_trabajador)
    elif opcion == '5':
        print("Regresando al menú principal...")
    else:
        print("Opción no válida, intente de nuevo.")   
    
    # hilo = threading.Thread(target=accion)
    # hilo.start()
    # hilo.join()







# Funciones para mostrar y realizar acciones en los menús
def mostrar_menu_doctor():
    print("\nMenú Doctor:")
    print("1. Cerrar visita de emergencia")
    print("5. Volver")

def realizar_accion_doctor(id_doctor, opcion):
    if opcion == '1':
        cerrar_visita_emergencia(id_doctor)
    else:
        print("Opción no válida, intente de nuevo.")







# Funciones para mostrar y realizar acciones en los menús
def mostrar_menu_utilidades():
    print("\nMenú Utilidades:")
    print("1. Listar nodos activos con sala de emergencia")
    print("2. Mostrar Log de cambios en la base de datos")
    print("3. Mostrar log de servidor")
    print("4. Mostrar Nodo Maestro")
    print("5. Mostrar changstomake")
    print("6. Volver")

def realizar_accion_utilidades(opcion):
    if opcion == '1':
        print("\nListando nodos activos con sala de emergencia")
        for node_id, client in active_connections.items():
            print(f"ID del nodo: {node_id}, IP: {client.getpeername()[0]}")
        log_message("[Utilidades] Listando nodos activos con sala de emergencia.")
    elif opcion == '2':
        print("\nMostrando Log de cambios en la base de datos")
        mostrar_log_base_datos()  # Llamar a la función para mostrar log de base de datos
        log_message("[Utilidades] Mostrando Log de cambios en la base de datos.")
    elif opcion == '3':
        print("\nMostrando Log de servidor")
        mostrar_log_servidor()  # Llamar a la función para mostrar log de servidor
        log_message("[Utilidades] Mostrando Log de servidor.")
    elif opcion == '4':
        print("\nMostrando Nodo Maestro")
        obtener_nodo_maestro() # Llamar a la función para mostrar nodo maestro
        log_message("[Utilidades] Mostrando Nodo Maestro.")
    elif opcion == '5':
        print("\nMostrando changetomake")
        mostrar_log_changestomake()  # Llamar a la función para mostrar log de base de datos
        log_message("[Utilidades] Mostrando Log de cambios en la base de datos.")
    else:
        print("Opción no válida, intente de nuevo.")





# Funciones para mostrar y realizar acciones en los menús
def mostrar_menu_tablas():
    print("\nMenú Tablas:")
    print("1. Mostrar tabla Salas de Emergencia")
    print("2. Mostrar tabla Doctores")
    print("3. Mostrar tabla Camas")
    print("4. Mostrar tabla Pacientes")
    print("5. Mostrar tabla Visitas")
    print("7. Mostrar tabla Trabajadores")
    print("8. Volver")

def realizar_accion_tablas(opcion):
    if opcion == '1':
        print("\nMostrando tabla Salas de Emergencia")
        listar_salas_emergencia()
        log_message("[Tablas] Mostrando tabla de Salas de Emergencias.")
    elif opcion == '2':
        print("\nMostrando tabla Doctores")
        listar_doctores()
        log_message("[Tablas] Mostrando tabla de Doctores.")
    elif opcion == '3':
        print("\nMostrando tabla Camas")
        listar_camas()
        log_message("[Tablas] Mostrando tabla de Camas.")
    elif opcion == '4':
        print("\nMostrando tabla Pacientes")
        listar_pacientes()
        log_message("[Tablas] Mostrando tabla de Pacientes.")
    elif opcion == '5':
        print("\nMostrando tabla Visitas")
        listar_visitas()
        log_message("[Tablas] Mostrando tabla de Visitas.")
    elif opcion == '7':
        print("\nMostrando tabla Trabajadores")
        listar_trabajadores_sociales()
        log_message("[Tablas] Mostrando tabla de Trabajadores.")
    elif opcion == '8':
        print("Regresando al menú principal...")
    else:
        print("Opción no válida, intente de nuevo.")

def mostrar_menu_admin():
    print("\nMenú Admin:")
    print("1. Registrar doctor")
    print("2. Registrar paciente")
    print("3. Registrar trabajador social")
    print("4. Actualizar doctor")
    print("5. Actualizar paciente")
    print("6. Actualizar trabajador social")
    print("7. Volver")

def realizar_accion_admin(opcion):
    if opcion == '1':
        print("\nRegistrar doctor")
        agregar_doctor()
    elif opcion == '2':
        print("\nRegistrar paciente")
        agregar_paciente()
    elif opcion == '3':
        print("\nRegistrar trabajador social")
        agregar_trabajador()
    elif opcion == '4':
        print("\nActualizar doctor")
        actualizar_doctor()
    elif opcion == '5':
        print("\nActualizar paciente")
        actualizar_paciente()
    elif opcion == '6':
        print("\nActualizar trabajador social")
        actualizar_trabajador()
    elif opcion == '7':
        print("Regresando al menú principal...")
    else:
        print("Opción no válida, intente de nuevo.")
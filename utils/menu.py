from models.emergency_room import listar_salas_emergencia
from models.doctors import listar_doctores
from controllers.database import mostrar_log_base_datos, mostrar_log_servidor

def mostrar_menu():
    print("\n\nMenú:")
    print("1. Trabajador Social")
    print("2. Doctor")
    print("3. Utilidades")
    print("4. Salir")




# Funciones para mostrar y realizar acciones en los menús
def mostrar_menu_trabajador_social():
    print("\nMenú Trabajador Social:")
    print("1. Registrar visita emergencia")
    print("2. Listar Salas de Emergencia")
    print("3. Listar Doctores")
    print("5. Volver")

def realizar_accion_trabajador_social(opcion):
    if opcion == '1':
        print("\nRegistrar visita emergencia")
    elif opcion == '2':
        print("\nListando Salas de Emergencia")
        listar_salas_emergencia()  # Llamar a la función para listar salas de emergencia
    elif opcion == '3':
        print("\nListando Doctores")
        listar_doctores()
    else:
        print("Opción no válida, intente de nuevo.")



# Funciones para mostrar y realizar acciones en los menús
def mostrar_menu_doctor():
    print("\nMenú Doctor:")
    print("1. Cerrar visita emergencia")
    print("5. Volver")

def realizar_accion_doctor(opcion):
    if opcion == '1':
        print("Cerrar visita emergencia")
    else:
        print("Opción no válida, intente de nuevo.")



# Funciones para mostrar y realizar acciones en los menús
def mostrar_menu_utilidades():
    print("\nMenú Utilidades:")
    print("1. Listar nodos activos con sala de emergencia")
    print("2. Mostrar Log de cambios en la base de datos")
    print("3. Mostrar log de servidor")
    print("4. Mostrar Nodo Maestro")
    print("5. Volver")

def realizar_accion_utilidades(opcion):
    if opcion == '1':
        print("\nListando nodos activos con sala de emergencia")
    elif opcion == '2':
        print("\nMostrando Log de cambios en la base de datos")
        mostrar_log_base_datos()  # Llamar a la función para mostrar log de base de datos
    elif opcion == '3':
        print("\nMostrando Log de servidor")
        mostrar_log_servidor()  # Llamar a la función para mostrar log de servidor
    else:
        print("Opción no válida, intente de nuevo.")
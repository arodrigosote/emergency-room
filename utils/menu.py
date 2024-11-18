from models.emergency_room import listar_salas_emergencia
from models.doctors import listar_doctores

def mostrar_menu():
    print("Menú:")
    print("1. Trabajador Social")
    print("2. Doctor")
    print("3. Salir")




# Funciones para mostrar y realizar acciones en los menús
def mostrar_menu_trabajador_social():
    print("\n\nMenú Trabajador Social:")
    print("1. Registrar visita emergencia")
    print("2. Listar Salas de Emergencia")
    print("3. Listar Doctores")
    print("5. Volver")

def realizar_accion_trabajador_social(opcion):
    if opcion == '1':
        print("Registrar visita emergencia")
    elif opcion == '2':
        print("Listando Salas de Emergencia")
        listar_salas_emergencia()  # Llamar a la función para listar salas de emergencia
    elif opcion == '3':
        print("Listando Doctores")
        listar_doctores()
    else:
        print("Opción no válida, intente de nuevo.")



# Funciones para mostrar y realizar acciones en los menús
def mostrar_menu_doctor():
    print("\n\nMenú Doctor:")
    print("1. Cerrar visita emergencia")
    print("5. Volver")

def realizar_accion_doctor(opcion):
    if opcion == '1':
        print("Cerrar visita emergencia")
    else:
        print("Opción no válida, intente de nuevo.")
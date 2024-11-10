def mostrar_menu():
    print("\n--- Menú Principal ---")
    print("1. Ejecutar controlador de ejemplo")
    print("2. Otra opción")
    print("3. Salir")
    opcion = input("Selecciona una opción: ")
    try:
        return int(opcion)
    except ValueError:
        print("Por favor ingresa un número.")
        return 0
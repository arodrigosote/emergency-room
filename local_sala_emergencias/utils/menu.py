def mostrar_menu():
    while True:
        print("\nSeleccione una de las siguientes opciones:")
        print("1. Enviar mensaje")
        print("2. Opción 2")
        print("3. Opción 3")
        opcion = input("Ingrese la opción: ")
        
        if opcion in ['1', '2', '3']:
            return opcion
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
from controllers.nodes import get_network_nodes

def opcion1():
    nodes = get_network_nodes()
    print("Nodos en la red:")
    for node in nodes:
        print(f"ID: {node['id']}, IP: {node['ip']}, MAC: {node['mac']}")

def opcion2():
    print("Opción 2 seleccionada")

def opcion3():
    print("Opción 3 seleccionada")

def opcion4():
    print("Opción 4 seleccionada")

def mostrar_menu():
    print("Menú:")
    print("1. Conectar nodos")
    print("2. Opción 2")
    print("3. Opción 3")
    print("4. Opción 4")
    print("5. Salir")

def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        if opcion == '1':
            opcion1()
        elif opcion == '2':
            opcion2()
        elif opcion == '3':
            opcion3()
        elif opcion == '4':
            opcion4()
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida, intente de nuevo.")

if __name__ == "__main__":
    main()



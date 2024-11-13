from controllers.server import iniciar_servidor
from controllers.client import conectar_a_servidor
from models.message import send_message
from utils.menu import mostrar_menu
import threading

def main():
    servidor_hilo = threading.Thread(target=iniciar_servidor)
    servidor_hilo.start()

    # Lista de direcciones IP de otros servidores
    servidores = ['192.168.1.2', '192.168.1.3']
    conexiones_activas = []

    for servidor in servidores:
        cliente_hilo = threading.Thread(target=conectar_a_servidor, args=(servidor, conexiones_activas))
        cliente_hilo.start()
        cliente_hilo.join()

    print(f"Servidores conectados: {[conn[0] for conn in conexiones_activas]}")

    # Mostramos menu
    opcion = mostrar_menu()
    print(f"Opción seleccionada: {opcion}")
    
    if opcion == '1':
        print("Seleccione al dispositivo que quiere enviar mensaje:")
        for i, (servidor, _) in enumerate(conexiones_activas):
            print(f"{i+1}. {servidor}")
        seleccion = int(input("Ingrese el número del dispositivo: ")) - 1
        mensaje = input("Ingrese el mensaje a enviar: ")
        send_message(conexiones_activas[seleccion][1], mensaje)
    elif opcion == '2':
        print("Opción 2")

    servidor_hilo.join()

if __name__ == "__main__":
    main()

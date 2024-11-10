from controllers.server import start_server
from controllers.client import start_client, send_message_to_device
from controllers.utils import print_connected_devices
from models.devices import get_connected_devices

def start_p2p():
    import threading
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Lista de direcciones IP a las que se conectará automáticamente
    ip_list = ["192.168.1.2", "192.168.1.3", "192.168.1.4"]

    for ip in ip_list:
        client_thread = threading.Thread(target=start_client, args=(ip,), daemon=True)
        client_thread.start()

    while True:
        option = input("\nOpciones: \n1. Mostrar dispositivos conectados\n2. Mandar mensaje a dispositivo\n3. Salir\nElige una opción: ").strip()
        
        if option == "1":
            print_connected_devices()
        elif option == "2":
            device_ip = input("Ingresa la IP del dispositivo al que deseas enviar un mensaje: ")
            message = input("Escribe el mensaje: ")
            send_message_to_device(device_ip, message)
        elif option == "3":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    start_p2p()
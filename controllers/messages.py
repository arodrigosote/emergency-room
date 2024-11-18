
from main import active_connections

def enviar_mensaje_a_nodo(mensaje, nodo_id):
    """
    Envía un mensaje a un nodo específico identificado por su ID.

    :param mensaje: El mensaje a enviar.
    :param nodo_id: El ID del nodo de destino.
    """

    try:
        destino = int(nodo_id)
        if destino in active_connections:
            client_socket = active_connections[destino]
            if client_socket.fileno() != -1:  # Verifica que el socket siga activo
                client_socket.send(mensaje.encode())
                print(f"[Mensaje enviado] A nodo {destino}: {mensaje}")
            else:
                print(f"[Error] La conexión con el nodo {destino} no está activa.")
        else:
            print(f"[Error] Nodo {destino} no está conectado.")
    except Exception as e:
        print(f"[Error] No se pudo enviar el mensaje: {e}")

from controllers.server_client import active_connections

def enviar_mensaje_a_nodo(mensaje, nodo_id):
    """
    Envía un mensaje a un nodo específico identificado por su ID.

    :param mensaje: El mensaje a enviar.
    :param nodo_id: El ID del nodo de destino.
    """
    conn = active_connections.get(nodo_id)
    if conn:
        try:
            conn.sendall(mensaje.encode('utf-8'))
            print(f"Mensaje enviado a nodo {nodo_id}")
        except Exception as e:
            print(f"Error al enviar mensaje a nodo {nodo_id}: {e}")
    else:
        print(f"Nodo {nodo_id} no está conectado.")
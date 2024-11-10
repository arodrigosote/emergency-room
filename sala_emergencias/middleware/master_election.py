import threading

class MasterElection:
    def __init__(self, node_id, other_node_ids):
        self.node_id = node_id
        self.other_node_ids = other_node_ids
        self.master_id = None
        self.lock = threading.Lock()

    def start(self):
        # Inicializar cualquier recurso necesario para la elección
        pass

    def start_election(self):
        print(f"Nodo {self.node_id} iniciando elección.")
        higher_nodes = [node_id for node_id in self.other_node_ids if node_id > self.node_id]
        
        if not higher_nodes:
            self.become_master()
        else:
            for node_id in higher_nodes:
                # Enviar mensaje de elección al nodo con ID mayor
                print(f"Enviando mensaje de elección al nodo {node_id}")
                # Aquí se debería implementar la lógica de comunicación entre nodos
                # Simulación de respuesta de los nodos mayores
                response = self.receive_response(node_id)
                if response == "OK":
                    return

        # Si no se recibe respuesta de ningún nodo con ID mayor, este nodo se convierte en el maestro
        self.become_master()

    def receive_response(self, node_id):
        # Simulación de la recepción de una respuesta de un nodo mayor
        # En una implementación real, esto debería manejar la comunicación de red
        return "OK" if node_id > self.node_id else None

    def become_master(self):
        with self.lock:
            self.master_id = self.node_id
            print(f"Nodo {self.node_id} se ha convertido en el maestro.")
            self.notify_all_nodes()

    def notify_all_nodes(self):
        for node_id in self.other_node_ids:
            print(f"Notificando al nodo {node_id} que el nodo {self.node_id} es el maestro.")
            # Aquí se debería implementar la lógica de comunicación para notificar a los otros nodos

    def is_master(self):
        with self.lock:
            return self.master_id == self.node_id
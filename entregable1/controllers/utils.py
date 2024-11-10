from datetime import datetime
from models.devices import get_connected_devices

def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def print_connected_devices():
    devices = get_connected_devices()
    if devices:
        print("Dispositivos conectados:")
        for device in devices:
            print(f"- {device}")
    else:
        print("No hay dispositivos conectados.")
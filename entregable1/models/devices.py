# List and dictionary to store connected devices and connections
connected_devices = []
client_sockets = {}

def add_connected_device(device):
    connected_devices.append(device)

def remove_connected_device(device):
    connected_devices.remove(device)

def get_connected_devices():
    return connected_devices

def get_client_sockets():
    return client_sockets
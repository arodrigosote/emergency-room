from datetime import datetime

# Dictionaries to store messages
received_messages = {}
sent_messages = {}

def add_received_message(ip, message):
    timestamp = get_current_timestamp()
    if ip not in received_messages:
        received_messages[ip] = []
    received_messages[ip].append(f"{timestamp} - {message}")

def add_sent_message(ip, message):
    timestamp = get_current_timestamp()
    if ip not in sent_messages:
        sent_messages[ip] = []
    sent_messages[ip].append(f"{timestamp} - {message}")

def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
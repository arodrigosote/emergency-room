#!/bin/bash

# Verifica que el script se ejecute como root
if [ "$(id -u)" -ne 0 ]; then
    echo "Este script debe ejecutarse como root. Usa 'sudo' para ejecutarlo."
    exit 1
fi

# Verifica que se pase un parámetro
if [ "$#" -ne 1 ]; then
    echo "Uso: $0 <nodo>"
    echo "Nodos disponibles:"
    echo "  nodo1 - Asigna IP 192.168.174.140"
    echo "  nodo2 - Asigna IP 192.168.174.141"
    echo "  nodo3 - Asigna IP 192.168.174.142"
    exit 1
fi

# Detecta automáticamente una interfaz de red activa (excluyendo loopback)
INTERFAZ=$(ip -o link show | awk -F': ' '{print $2}' | grep -v lo | head -n 1)

if [ -z "$INTERFAZ" ]; then
    echo "No se encontró una interfaz de red activa. Asegúrate de estar conectado a una red."
    exit 1
fi

echo "Se detectó la interfaz activa: $INTERFAZ"

# Asigna la IP según el nodo
case "$1" in
    nodo1)
        IP="192.168.174.140"
        ;;
    nodo2)
        IP="192.168.174.141"
        ;;
    nodo3)
        IP="192.168.174.142"
        ;;
    *)
        echo "Nodo no válido: $1"
        echo "Uso: $0 <nodo>"
        echo "Nodos disponibles:"
        echo "  nodo1 - Asigna IP 192.168.174.140"
        echo "  nodo2 - Asigna IP 192.168.174.141"
        echo "  nodo3 - Asigna IP 192.168.174.142"
        exit 1
        ;;
esac

# Cambia solo la dirección IP de la interfaz detectada
echo "Configurando la interfaz $INTERFAZ con la IP $IP..."
ip addr flush dev "$INTERFAZ"
ip addr add "$IP" dev "$INTERFAZ"

# Verifica el cambio
echo "Nueva configuración de red para $INTERFAZ:"
ip addr show "$INTERFAZ"

echo "La dirección IP se ha cambiado exitosamente a $IP."

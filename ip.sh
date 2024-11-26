#!/bin/bash

# Verifica que el script se ejecute como root
if [ "$(id -u)" -ne 0 ]; then
    echo "Este script debe ejecutarse como root. Usa 'sudo' para ejecutarlo."
    exit 1
fi

# Verifica que se pase un parámetro
if [ "$#" -ne 1 ]; then
    echo "Uso: $0 <opcion>"
    echo "Opciones disponibles:"
    echo "  opcion1 - Asigna IP 192.168.1.100"
    echo "  opcion2 - Asigna IP 192.168.1.101"
    exit 1
fi

# Detecta automáticamente una interfaz de red activa (excluyendo loopback)
INTERFAZ=$(ip -o link show | awk -F': ' '{print $2}' | grep -v lo | head -n 1)

if [ -z "$INTERFAZ" ]; then
    echo "No se encontró una interfaz de red activa. Asegúrate de estar conectado a una red."
    exit 1
fi

echo "Se detectó la interfaz activa: $INTERFAZ"

# Asigna la IP según el parámetro
case "$1" in
    opcion1)
        IP="192.168.1.100"
        ;;
    opcion2)
        IP="192.168.1.101"
        ;;
    *)
        echo "Opción no válida: $1"
        echo "Uso: $0 <opcion>"
        echo "Opciones disponibles:"
        echo "  opcion1 - Asigna IP 192.168.1.100"
        echo "  opcion2 - Asigna IP 192.168.1.101"
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

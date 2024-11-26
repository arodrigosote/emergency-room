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

# Interface de red (cambia 'eth0' por el nombre de tu interfaz de red)
INTERFAZ="eth0"

# Asigna la IP según el parámetro
case "$1" in
    opcion1)
        IP="192.168.174.140"
        ;;
    opcion2)
        IP="192.168.174.141"
        ;;
    opcion3)
        IP="192.168.174.142"
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

# Cambia solo la dirección IP de la interfaz
echo "Configurando la interfaz $INTERFAZ con la IP $IP..."
ip addr flush dev "$INTERFAZ"
ip addr add "$IP" dev "$INTERFAZ"

# Verifica el cambio
echo "Nueva configuración de red para $INTERFAZ:"
ip addr show "$INTERFAZ"

echo "La dirección IP se ha cambiado exitosamente a $IP."

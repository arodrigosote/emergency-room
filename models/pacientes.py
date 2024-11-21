import sqlite3
import os

def listar_pacientes():
    # Lista todos los pacientes en la base de datos y los muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pacientes')
    pacientes = cursor.fetchall()
    conn.close()

    # Mostrar los pacientes en una tabla por consola sin utilizar tabulate
    headers = ["ID Paciente", "Nombre", "Edad", "Diagnóstico"]
    print(f"{headers[0]:<12} {headers[1]:<20} {headers[2]:<5} {headers[3]:<30}")
    print("-" * 70)
    for paciente in pacientes:
        print(f"{paciente[0]:<12} {paciente[1]:<20} {paciente[2]:<5} {paciente[3]:<30}")
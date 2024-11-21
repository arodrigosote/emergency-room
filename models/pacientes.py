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
    headers = ["ID Paciente", "Nombre", "Género", "Tipo de Sangre", "Alergias", "Fecha de Registro"]
    print(f"{headers[0]:<12} {headers[1]:<20} {headers[2]:<7} {headers[3]:<15} {headers[4]:<30} {headers[5]:<20}")
    print("-" * 110)
    for paciente in pacientes:
        print(f"{paciente[0]:<12} {paciente[1]:<20} {paciente[2]:<7} {paciente[3]:<15} {paciente[4]:<30} {paciente[5]:<20}")
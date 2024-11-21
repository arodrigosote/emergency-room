import sqlite3
import os

def listar_doctores():
    # Lista todos los doctores en la base de datos y los muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM doctores')
    doctores = cursor.fetchall()
    conn.close()

    # Mostrar los doctores en una tabla por consola sin utilizar tabulate
    headers = ["ID Doctor", "Nombre", "Especialidad", "Turno"]
    print(f"{headers[0]:<10} {headers[1]:<20} {headers[2]:<20} {headers[3]:<10}")
    print("-" * 65)
    for doctor in doctores:
        print(f"{doctor[0]:<10} {doctor[1]:<20} {doctor[2]:<20} {doctor[3]:<10}")
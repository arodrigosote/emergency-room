import sqlite3
import os


def listar_trabajadores_sociales():
    # Lista todos los trabajadores sociales en la base de datos y los muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trabajadores_sociales')
    trabajadores = cursor.fetchall()
    conn.close()

    # Mostrar los trabajadores sociales en una tabla por consola sin utilizar tabulate
    headers = ["ID Trabajador", "Nombre"]
    print(f"{headers[0]:<15} {headers[1]:<20}")
    print("-" * 35)
    for trabajador in trabajadores:
        print(f"{trabajador[0]:<15} {trabajador[1]:<20}")
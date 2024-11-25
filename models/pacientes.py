import sqlite3
import os
from utils.log import log_message, log_database
from models.node import procesar_consulta

def listar_pacientes():
    # Lista todos los pacientes en la base de datos y los muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pacientes')
    pacientes = cursor.fetchall()
    conn.close()

    # Mostrar los pacientes en una tabla por consola sin utilizar tabulate
    headers = ["ID Paciente", "Nombre", "Género", "Tipo de Sangre", "Alergias", "Fecha de Registro"]
    print(f"{headers[0]:<12} {headers[1]:<20} {headers[2]:<10} {headers[3]:<15} {headers[4]:<30} {headers[5]:<20}")
    print("-" * 110)
    for paciente in pacientes:
        genero = "Hombre" if paciente[2] == '0' else "Mujer"
        print(f"{paciente[0]:<12} {paciente[1]:<20} {genero:<10} {paciente[3]:<15} {paciente[4]:<30} {paciente[5]:<20}")

def agregar_paciente():
    try:
        # Solicitar datos del paciente
        nombre = input("Ingrese el nombre del paciente: ")
        genero = input("Ingrese el género del paciente (0 para Hombre, 1 para Mujer): ")
        tipo_sangre = input("Ingrese el tipo de sangre del paciente: ")
        alergias = input("Ingrese las alergias del paciente: ")

        # Agrega un nuevo paciente a la base de datos
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pacientes (nombre, genero, tipo_sangre, alergias)
            VALUES (?, ?, ?, ?)
        ''', (nombre, genero, tipo_sangre, alergias))
        conn.commit()
        conn.close()
        mensaje = f"INSERT INTO pacientes (nombre, genero, tipo_sangre, alergias) VALUES ('{nombre}', {genero}, '{tipo_sangre}', '{alergias}')"
        log_database(f"# {mensaje}")
        procesar_consulta(mensaje)
        log_message(f"[Base de Datos] Paciente '{nombre}' agregado a la base de datos.")
        print(f"Paciente '{nombre}' agregado a la base de datos.")
    except sqlite3.Error as e:
        log_message(f"Error al agregar paciente: {e}")
        print(f"Error al agregar paciente: {e}")

def actualizar_paciente():
    listar_pacientes()
    id_paciente = input("Ingrese el ID del paciente a actualizar: ")
    
    # Validar si el ID existe en la base de datos
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM pacientes WHERE id_paciente = ?', (id_paciente,))
        if cursor.fetchone()[0] == 0:
            log_message(f"[Error] El ID {id_paciente} no existe en la base de datos.")
            print(f"El ID {id_paciente} no existe en la base de datos.")
            conn.close()
            return
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo validar el ID del paciente: {e}")
        print(f"Error al validar el ID del paciente: {e}")
        conn.close()
        return
    
    nuevo_nombre = input("Ingrese el nuevo nombre del paciente: ")
    nuevo_genero = input("Ingrese el nuevo género del paciente (0 para Hombre, 1 para Mujer): ")
    nuevo_tipo_sangre = input("Ingrese el nuevo tipo de sangre del paciente: ")
    nuevas_alergias = input("Ingrese las nuevas alergias del paciente: ")
    nueva_fecha_registro = input("Ingrese la nueva fecha de registro (YYYY-MM-DD): ")
    
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        
        query = """
            UPDATE pacientes
            SET nombre = ?, genero = ?, tipo_sangre = ?, alergias = ?, fecha_registro = ?
            WHERE id_paciente = ?
        """
        
        cursor.execute(query, (nuevo_nombre, nuevo_genero, nuevo_tipo_sangre, nuevas_alergias, nueva_fecha_registro, id_paciente))
        conn.commit()
        mensaje = f"UPDATE pacientes SET nombre = '{nuevo_nombre}', genero = {nuevo_genero}, tipo_sangre = '{nuevo_tipo_sangre}', alergias = '{nuevas_alergias}', fecha_registro = '{nueva_fecha_registro}' WHERE id_paciente = {id_paciente}"
        log_database(f"# {mensaje}")
        procesar_consulta(mensaje)
        log_message(f"[Base de Datos] Paciente {nuevo_nombre} actualizado en la base de datos.")
        print(f"Paciente {nuevo_nombre} actualizado en la base de datos.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo actualizar el paciente: {e}")
        print(f"Error al actualizar el paciente: {e}")
    finally:
        conn.close()
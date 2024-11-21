import sqlite3
import os
from utils.log import log_message
from datetime import datetime
from models.node import enviar_mensaje_a_todos, enviar_consulta_sencilla

def listar_visitas():
    # Lista todas las visitas en la base de datos y las muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM visitas_emergencia')
    visitas = cursor.fetchall()
    conn.close()

    # Mostrar las visitas en una tabla por consola sin utilizar tabulate
    headers = ["ID Visita", "ID Paciente", "Fecha", "Motivo"]
    print(f"{headers[0]:<10} {headers[1]:<12} {headers[2]:<15} {headers[3]:<30}")
    print("-" * 70)
    for visita in visitas:
        print(f"{visita[0]:<10} {visita[1]:<12} {visita[2]:<15} {visita[3]:<30}")

def agregar_visita():
    try:
        # Obtener datos del paciente
        paciente_id = input("Ingrese el ID del paciente: ")
        motivo = input("Ingrese el motivo de la visita: ")
        # Verificar si el paciente ya está registrado
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE id_paciente = ?", (paciente_id,))
        paciente = cursor.fetchone()

        if not paciente:
            # Si el paciente no está registrado, pedir los datos para registrarlo
            print("El paciente no está registrado. Por favor, ingrese los datos del paciente.")
            nombre = input("Ingrese el nombre del paciente: ")
            genero = int(input("0. Hombre\n1.Mujer\nSeleccione una opción: "))
            if genero != 0 and genero != 1:
                print("Opción inválida.")
                return
            tipo_sangre = input("Ingrese el tipo de sangre: ")
            alergias = input("Ingrese las alergias (opcional): ")
            if not alergias:
                alergias = 'None'

            # Insertar el nuevo paciente en la base de datos
            query_paciente = """
            INSERT INTO pacientes (nombre, genero, tipo_sangre, alergias) 
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(query_paciente, (nombre, genero, tipo_sangre, alergias))
            conn.commit()
            mensaje = f"INSERT INTO pacientes (nombre, genero, tipo_sangre, alergias) VALUES ('{nombre}', {genero}, '{tipo_sangre}', '{alergias}')"
            enviar_consulta_sencilla(mensaje)

            
            log_message("[Base de Datos] Nuevo paciente registrado en la base de datos.")
        else:
            log_message("[Base de Datos] Paciente ya registrado en la base de datos.")

    
        # # Obtener doctores disponibles
        # cursor.execute("SELECT id_doctor, nombre FROM doctores WHERE estado = 'disponible'")
        # doctores_disponibles = cursor.fetchall()
        # if not doctores_disponibles:
        #     print("No hay doctores disponibles en este momento.")
        #     return

        # # Mostrar doctores disponibles y seleccionar uno
        # print("Doctores disponibles:")
        # for doctor in doctores_disponibles:
        #     print(f"ID: {doctor[0]}, Nombre: {doctor[1]}")
        # id_doctor = input("Seleccione el ID del doctor: ")

        # # Recibir el atributo del trabajador social
        # id_trabajador_social = input("Ingrese el ID del trabajador social: ")

        # # Generar timestamp para la fecha de salida
        # fecha_salida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # # Datos de la visita
        # visita = (paciente_id, motivo, id_doctor, id_trabajador_social, fecha_salida)

        # # Insertar la visita en la base de datos
        # query = """
        #     INSERT INTO visitas_emergencia (id_paciente, motivo, id_doctor, id_trabajador_social, fecha_salida) 
        #     VALUES (?, ?, ?, ?, ?)
        # """
        # cursor.execute(query, visita)
        # conn.commit()
        # log_message("[Base de Datos] Visita de emergencia agregada a la base de datos.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo agregar la visita de emergencia: {e}")
    finally:
        conn.close()
import sqlite3
import os
from utils.log import log_message, log_database
from datetime import datetime
from models.node import procesar_consulta
from models.emergency_room import obtener_sala_y_cama

def listar_visitas():
    # Lista todas las visitas en la base de datos y las muestra en una tabla por consola
    conn = sqlite3.connect('nodos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id_visita, folio, motivo, id_paciente, id_doctor, id_sala, id_cama, id_trabajador_social, fecha_salida, estado FROM visitas_emergencia')
    visitas = cursor.fetchall()
    conn.close()

    # Mostrar las visitas en una tabla por consola sin utilizar tabulate
    headers = ["ID Visita", "Folio", "Motivo", "ID Paciente", "ID Doctor", "ID Sala", "ID Cama", "ID Trabajador Social", "Fecha Salida", "Estado"]
    print(f"{headers[0]:<10} {headers[1]:<15} {headers[2]:<30} {headers[3]:<12} {headers[4]:<10} {headers[5]:<8} {headers[6]:<8} {headers[7]:<20} {headers[8]:<20} {headers[9]:<10}")
    print("-" * 160)
    for visita in visitas:
        print(f"{visita[0]:<10} {visita[1]:<15} {visita[2]:<30} {visita[3]:<12} {visita[4]:<10} {visita[5]:<8} {visita[6]:<8} {visita[7]:<20} {visita[8]:<20} {visita[9]:<10}")

def agregar_visita(id_trabajador):
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
            genero = int(input("0. Hombre\n1. Mujer\nSeleccione una opción: "))
            if genero != 0 and genero != 1:
                print("Opción inválida.")
                return
            tipo_sangre = input("Ingrese el tipo de sangre: ")
            alergias = input("Ingrese las alergias (opcional): ")
            if not alergias:
                alergias = 'None'


            # Insertar los datos del paciente
            cursor.execute("""
                INSERT INTO pacientes (nombre, genero, tipo_sangre, alergias) 
                VALUES (?, ?, ?, ?)
            """, (nombre, genero, tipo_sangre, alergias))
            
            # Obtener el ID del nuevo paciente
            paciente_id = cursor.lastrowid  # Obtiene el id del último registro insertado
            conn.commit()


            mensaje = f"INSERT INTO pacientes (nombre, genero, tipo_sangre, alergias) VALUES ('{nombre}', {genero}, '{tipo_sangre}', '{alergias}')"
            log_database(f"# INSERT INTO pacientes (nombre, genero, tipo_sangre, alergias) VALUES ('{nombre}', {genero}, '{tipo_sangre}', '{alergias}')")
            procesar_consulta(mensaje)

            
            log_message("[Base de Datos] Nuevo paciente registrado en la base de datos.")
            print(f"Paciente registrado con ID: {paciente_id}")
        else:
            log_message("[Base de Datos] Paciente ya registrado en la base de datos.")

    
        # Obtener doctores disponibles
        cursor.execute("SELECT id_doctor, nombre FROM doctores WHERE estado = 'disponible'")
        doctores_disponibles = cursor.fetchall()
        if not doctores_disponibles:
            print("\nNo hay doctores disponibles en este momento.")
            return

        # Mostrar doctores disponibles y seleccionar uno
        print("\nDoctores disponibles:")
        for doctor in doctores_disponibles:
            print(f"ID: {doctor[0]}, Nombre: {doctor[1]}")
        id_doctor = input("Seleccione el ID del doctor: ")

        # Generar timestamp para la fecha de salida
        fecha_salida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Obtener sala y cama disponibles
        id_sala, id_cama = obtener_sala_y_cama()
        log_message(f"[Base de Datos] Sala y cama asignadas: {id_sala}, {id_cama}")
        
        # Insertar la visita en la base de datos
        cursor.execute("""
            INSERT INTO visitas_emergencia 
            (id_paciente, motivo, id_sala, id_cama, id_doctor, id_trabajador_social, fecha_salida) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (paciente_id, motivo, id_sala, id_cama, id_doctor, id_trabajador, fecha_salida))
        conn.commit()

        consulta = f"INSERT INTO visitas_emergencia (id_paciente, motivo, id_sala, id_cama, id_doctor, id_trabajador_social, fecha_salida) VALUES ({paciente_id}, '{motivo}', {id_sala}, {id_cama}, {id_doctor}, {id_trabajador}, '{fecha_salida}')"
        log_database(f"# {consulta}")
        procesar_consulta(consulta)
        log_message("[Base de Datos] Visita de emergencia agregada a la base de datos.")
        print("\nVisita de emergencia agregada con éxito.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo agregar la visita de emergencia: {e}")
    finally:
        conn.close()

def cerrar_visita_emergencia(id_doctor):
    try:
        conn = sqlite3.connect('nodos.db')
        cursor = conn.cursor()

        # Obtener visitas de emergencia en curso
        cursor.execute("SELECT id_visita, folio FROM visitas_emergencia WHERE id_doctor = ? AND estado = 'activa'", (id_doctor,))
        visita = cursor.fetchall()
        if not visita:
            print("No hay visitas de emergencia en curso para este doctor.")
            return

        # Mostrar visitas de emergencia en curso y seleccionar una
        print("\nVisita de emergencia activa:")
        print(f"ID Visita: {visita}")
        
        id_visita = visita[0][0]

        # Generar timestamp para la fecha de salida
        fecha_salida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Actualizar la visita de emergencia
        cursor.execute("UPDATE visitas_emergencia SET fecha_salida = ?, estado = 'cerrada' WHERE id_visita = ?", (fecha_salida, id_visita))
        conn.commit()

        mensaje = f"UPDATE visitas_emergencia SET fecha_salida = '{fecha_salida}', estado = 'cerrada' WHERE id_visita = {id_visita}"
        procesar_consulta(mensaje)
        log_database(f"# {mensaje}")
        log_message("[Base de Datos] Visita de emergencia cerrada.")
        print("\nVisita de emergencia cerrada con éxito.")
    except sqlite3.Error as e:
        log_message(f"[Error] No se pudo cerrar la visita de emergencia: {e}")
    finally:
        conn.close() 
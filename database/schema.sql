-- Eliminar la base de datos si ya está creada (descomentar para usar)
-- DROP DATABASE IF EXISTS nodos;

-- Crear la base de datos si no está creada
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- Creación de tablas principales

-- Tabla de Salas de Emergencia (Nodos)
CREATE TABLE IF NOT EXISTS salas_emergencia (
    id_sala INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    estado VARCHAR(20) DEFAULT 'activo', -- activo/inactivo
    es_maestro BOOLEAN DEFAULT 0,
    capacidad_total INTEGER NOT NULL,
    capacidad_disponible INTEGER NOT NULL
);

-- Tabla de Doctores
CREATE TABLE IF NOT EXISTS doctores (
    id_doctor INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'disponible' -- disponible/ocupado
);

-- Tabla de Trabajadores Sociales
CREATE TABLE IF NOT EXISTS trabajadores_sociales (
    id_trabajador INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla de Pacientes
CREATE TABLE IF NOT EXISTS pacientes (
    id_paciente INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    genero CHAR(1),
    tipo_sangre VARCHAR(5),
    alergias TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Camas
CREATE TABLE IF NOT EXISTS camas (
    id_cama INTEGER PRIMARY KEY,
    id_sala INTEGER NOT NULL,
    numero_cama INTEGER NOT NULL,
    estado VARCHAR(20) DEFAULT 'disponible', -- disponible/ocupada
    FOREIGN KEY (id_sala) REFERENCES salas_emergencia(id_sala)
);

-- Tabla de Visitas de Emergencia
CREATE TABLE IF NOT EXISTS visitas_emergencia (
    id_visita INTEGER PRIMARY KEY,
    folio VARCHAR(50) UNIQUE NOT NULL,
    id_paciente INTEGER NOT NULL,
    id_doctor INTEGER NOT NULL,
    id_sala INTEGER NOT NULL,
    id_cama INTEGER NOT NULL,
    id_trabajador_social INTEGER NOT NULL,
    fecha_salida TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'activa', -- activa/cerrada
    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente),
    FOREIGN KEY (id_doctor) REFERENCES doctores(id_doctor),
    FOREIGN KEY (id_sala) REFERENCES salas_emergencia(id_sala),
    FOREIGN KEY (id_cama) REFERENCES camas(id_cama),
    FOREIGN KEY (id_trabajador_social) REFERENCES trabajadores_sociales(id_trabajador)
);

-- Tabla para el control de distribución de visitas
CREATE TABLE IF NOT EXISTS control_distribucion (
    id_control INTEGER PRIMARY KEY,
    id_sala INTEGER NOT NULL,
    total_visitas_activas INTEGER DEFAULT 0,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_sala) REFERENCES salas_emergencia(id_sala)
);

-- Tabla para el registro de cambios y sincronización
CREATE TABLE IF NOT EXISTS log_cambios (
    id_log INTEGER PRIMARY KEY,
    tabla_afectada VARCHAR(50) NOT NULL,
    id_registro INTEGER NOT NULL,
    tipo_operacion VARCHAR(20) NOT NULL, -- INSERT/UPDATE/DELETE
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_sincronizacion VARCHAR(20) DEFAULT 'pendiente', -- pendiente/completado
    nodo_origen INTEGER NOT NULL,
    FOREIGN KEY (nodo_origen) REFERENCES salas_emergencia(id_sala)
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_visitas_estado ON visitas_emergencia(estado);
CREATE INDEX IF NOT EXISTS idx_doctores_estado ON doctores(estado);
CREATE INDEX IF NOT EXISTS idx_camas_estado ON camas(estado);
CREATE INDEX IF NOT EXISTS idx_log_cambios_estado ON log_cambios(estado_sincronizacion);

-- Triggers para mantener la integridad y consistencia

-- Trigger para generar el folio de visita
CREATE TRIGGER IF NOT EXISTS generar_folio_visita
AFTER INSERT ON visitas_emergencia
BEGIN
    UPDATE visitas_emergencia 
    SET folio = (
        NEW.id_paciente || '_' || 
        NEW.id_doctor || '_' || 
        NEW.id_sala || '_' || 
        NEW.id_visita
    )
    WHERE id_visita = NEW.id_visita;
END;

-- Trigger para actualizar capacidad disponible de sala
CREATE TRIGGER IF NOT EXISTS actualizar_capacidad_sala
AFTER INSERT ON visitas_emergencia
BEGIN
    UPDATE salas_emergencia 
    SET capacidad_disponible = capacidad_disponible - 1
    WHERE id_sala = NEW.id_sala;
END;

-- Trigger para registrar cambios en el log
CREATE TRIGGER IF NOT EXISTS registrar_cambio_visita
AFTER INSERT OR UPDATE ON visitas_emergencia
BEGIN
    INSERT INTO log_cambios (tabla_afectada, id_registro, tipo_operacion, nodo_origen)
    VALUES ('visitas_emergencia', NEW.id_visita, 
            CASE WHEN OLD.id_visita IS NULL THEN 'INSERT' ELSE 'UPDATE' END,
            NEW.id_sala);
END;

COMMIT;
PRAGMA foreign_keys = ON;
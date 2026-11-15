-- Catalogo de comodidades: datos de referencia opcionales para desarrollo.
-- Ejecutar despues de 01_esquema_alquiler.sql. Repetible sin duplicados.
INSERT INTO alquiler.comodidades (nombre) VALUES
('Wi-Fi'), ('Agua caliente'), ('Cocina'), ('Amoblado'),
('Lavandería'), ('Baño privado'), ('Estacionamiento'), ('Seguridad')
ON CONFLICT (nombre) DO NOTHING;

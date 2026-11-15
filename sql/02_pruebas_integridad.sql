-- ================================================================
-- Pruebas aisladas de integridad (NO conservan datos al finalizar).
-- PRECONDICION: 01_esquema_alquiler.sql aplicado en DB DE PRUEBA.
-- Ejecutar por separado en la misma DB; no usar en produccion.
-- Las verificaciones se realizan dentro de una transaccion ROLLBACK.
-- ================================================================
BEGIN;
DO $pruebas$
DECLARE
    v_buscador BIGINT;
    v_arrendador BIGINT;
    v_admin BIGINT;
    v_alojamiento BIGINT;
    v_comodidad BIGINT;
    v_error_detectado BOOLEAN;
BEGIN
    INSERT INTO alquiler.usuarios (nombre_completo, correo, clave_hash, rol)
    VALUES ('Buscador temporal', 'buscador-demo@example.invalid', 'hash_prueba_no_real', 'buscador')
    RETURNING usuario_id INTO v_buscador;
    INSERT INTO alquiler.buscadores (usuario_id) VALUES (v_buscador);

    INSERT INTO alquiler.usuarios (nombre_completo, correo, clave_hash, rol)
    VALUES ('Arrendador temporal', 'arrendador-demo@example.invalid', 'hash_prueba_no_real', 'arrendador')
    RETURNING usuario_id INTO v_arrendador;
    INSERT INTO alquiler.arrendadores (usuario_id, ruc)
    VALUES (v_arrendador, '20123456789');

    INSERT INTO alquiler.usuarios (nombre_completo, correo, clave_hash, rol)
    VALUES ('Admin temporal', 'admin-demo@example.invalid', 'hash_prueba_no_real', 'administrador')
    RETURNING usuario_id INTO v_admin;

    INSERT INTO alquiler.alojamientos
        (arrendador_id, titulo, descripcion, precio, direccion, distrito, tipo)
    VALUES (v_arrendador, 'Habitacion temporal', 'Solo prueba', 350.00,
            'Direccion de prueba', 'Distrito de prueba', 'habitacion')
    RETURNING alojamiento_id INTO v_alojamiento;

    INSERT INTO alquiler.comodidades (nombre)
    VALUES ('Comodidad temporal') RETURNING comodidad_id INTO v_comodidad;

    INSERT INTO alquiler.alojamiento_comodidades
        (alojamiento_id, comodidad_id) VALUES (v_alojamiento, v_comodidad);

    INSERT INTO alquiler.perfiles_companero
        (buscador_id, presupuesto_min, presupuesto_max)
    VALUES (v_buscador, 200.00, 500.00);

    INSERT INTO alquiler.verificaciones_identidad
        (usuario_id, ruta_documento, estado)
    VALUES (v_buscador, 'privado/documento-ficticio', 'pendiente');

    INSERT INTO alquiler.verificaciones_identidad
        (usuario_id, ruta_documento, estado, revisor_id, fecha_revision)
    VALUES (v_arrendador, 'privado/documento-ficticio-2', 'aprobada',
            v_admin, CURRENT_TIMESTAMP);

    INSERT INTO alquiler.registros_acceso (usuario_id, accion)
    VALUES (v_buscador, 'inicio_sesion');

    -- Prueba 1: no debe admitirse duplicidad de correo.
    v_error_detectado := FALSE;
    BEGIN
      INSERT INTO alquiler.usuarios (nombre_completo, correo, clave_hash, rol)
      VALUES ('Duplicado', 'buscador-demo@example.invalid', 'hash', 'buscador');
    EXCEPTION WHEN unique_violation THEN
      v_error_detectado := TRUE;
    END;
    IF NOT v_error_detectado THEN
      RAISE EXCEPTION 'FALLO prueba 1: correo duplicado admitido';
    END IF;

    -- Prueba 2: alojamiento sin arrendador real, FK.
    v_error_detectado := FALSE;
    BEGIN
      INSERT INTO alquiler.alojamientos
      (arrendador_id,titulo,descripcion,precio,direccion,distrito,tipo)
      VALUES (-999999, 'Invalido','Prueba', 100,'Dir','Distrito','habitacion');
    EXCEPTION WHEN foreign_key_violation THEN
      v_error_detectado := TRUE;
    END;
    IF NOT v_error_detectado THEN
      RAISE EXCEPTION 'FALLO prueba 2: FK no aplicada';
    END IF;

    -- Prueba 3: precio negativo.
    v_error_detectado := FALSE;
    BEGIN
      INSERT INTO alquiler.alojamientos
      (arrendador_id,titulo,descripcion,precio,direccion,distrito,tipo)
      VALUES (v_arrendador,'Invalido','Prueba',-2,'Dir','Distrito','habitacion');
    EXCEPTION WHEN check_violation THEN
      v_error_detectado := TRUE;
    END;
    IF NOT v_error_detectado THEN
      RAISE EXCEPTION 'FALLO prueba 3: precio invalido admitido';
    END IF;

    -- Prueba 4: solo un perfil de companero por buscador.
    v_error_detectado := FALSE;
    BEGIN
      INSERT INTO alquiler.perfiles_companero
      (buscador_id,presupuesto_min,presupuesto_max)
      VALUES (v_buscador,100,200);
    EXCEPTION WHEN unique_violation THEN
      v_error_detectado := TRUE;
    END;
    IF NOT v_error_detectado THEN
      RAISE EXCEPTION 'FALLO prueba 4: perfil duplicado admitido';
    END IF;

    -- Prueba 5: presupuestos invertidos.
    v_error_detectado := FALSE;
    BEGIN
      UPDATE alquiler.perfiles_companero
      SET presupuesto_min = 600, presupuesto_max = 200
      WHERE buscador_id = v_buscador;
    EXCEPTION WHEN check_violation THEN
      v_error_detectado := TRUE;
    END;
    IF NOT v_error_detectado THEN
      RAISE EXCEPTION 'FALLO prueba 5: presupuesto invalido admitido';
    END IF;

    -- Prueba 6: no se permite verificacion aprobada sin revisor y fecha.
    v_error_detectado := FALSE;
    BEGIN
      INSERT INTO alquiler.verificaciones_identidad
      (usuario_id,ruta_documento,estado)
      VALUES (v_buscador,'privado/invalido','aprobada');
    EXCEPTION WHEN check_violation THEN
      v_error_detectado := TRUE;
    END;
    IF NOT v_error_detectado THEN
      RAISE EXCEPTION 'FALLO prueba 6: revision inconsistente admitida';
    END IF;

    -- Prueba 7: estado de alojamiento restringido.
    v_error_detectado := FALSE;
    BEGIN
      UPDATE alquiler.alojamientos SET estado = 'desconocido'
      WHERE alojamiento_id = v_alojamiento;
    EXCEPTION WHEN check_violation THEN
      v_error_detectado := TRUE;
    END;
    IF NOT v_error_detectado THEN
      RAISE EXCEPTION 'FALLO prueba 7: estado invalido admitido';
    END IF;

    RAISE NOTICE 'OK: 7 pruebas de integridad satisfechas. Se revertiran los datos de prueba.';
END;
$pruebas$;
ROLLBACK;

"""Crear administrador inicial en forma interactiva dentro de backend.
Ejecutar: docker compose exec backend python -m scripts.crear_admin
"""
from getpass import getpass
from sqlalchemy.exc import IntegrityError
from configuracion.base_datos import SessionLocal
from modelos.usuario import Usuario
from repositorios.usuarios import RepositorioUsuariosSQLAlchemy
from seguridad.autenticacion import hash_clave

def main():
    correo = input('Correo administrador: ').strip().lower()
    nombre = input('Nombre completo: ').strip()
    clave = getpass('Contraseña segura (mínimo 10 caracteres): ')
    if '@' not in correo or len(nombre) < 2 or len(clave) < 10:
        print('Datos inválidos. No se creó ningún administrador.'); return
    with SessionLocal() as db:
        usuarios = RepositorioUsuariosSQLAlchemy(db)
        if usuarios.por_correo(correo):
            print('Ya existe una cuenta con ese correo.'); return
        usuarios.agregar(Usuario(nombre_completo=nombre,correo=correo,clave_hash=hash_clave(clave),rol='administrador',estado_cuenta='verificada'))
        try:
            db.commit()
            print('Administrador creado.')
        except IntegrityError:
            db.rollback()
            print('No se pudo crear: revisa duplicidades.')

if __name__ == '__main__': main()

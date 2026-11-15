# Plan de pruebas de aceptación inicial

| Caso | Entrada | Resultado esperado |
|---|---|---|
| Registro buscador | Correo nuevo y contraseña válida | 201 y rol buscador |
| Correo duplicado | Mismo correo | 409 |
| Inicio de sesión | Credenciales válidas | JWT |
| Acceso sin sesión | Ruta privada | 401 |
| Buscador intenta publicar | JWT buscador y POST alojamiento | 403 |
| Publicar precio 0 | JWT arrendador | 422 |
| Editar publicación ajena | Otro arrendador | 403 |
| Búsqueda pública | GET alojamientos sin token | 200 |
| Perfil duplicado | PUT repetido | Actualiza perfil anterior (único) |
| Revisión ya finalizada | Segundo POST revisión | 409 |
| Descargar DNI público | Intento sin rol administrador | 401/403 |
| Integridad SQL | Script de 7 casos | Aviso OK + ROLLBACK |

Las pruebas no deben utilizar DNIs reales ni archivos personales. Las evidencias de ejecución se agregarán al Capítulo VI del informe.

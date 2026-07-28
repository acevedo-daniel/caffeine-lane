# Reproducción local del legado

Fecha: 2026-07-28  
Rama: `modernize/00-baseline`

## Entorno reproducido

Se creó `.env` local e ignorado por Git con valores de desarrollo para la clave y Cloudinary. No contiene credenciales de producción y no se documentan sus valores aquí. Se creó `.venv` local, también ignorado.

Comandos ejecutados:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py loaddata initial_data.json
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
```

Resultado: la instalación, `pip check`, el chequeo Django, las migraciones y la carga del fixture terminaron correctamente. El fixture instaló 17 objetos (3 categorías, 12 posts y un usuario). El servidor respondió HTTP 200 para `/`, `/home/`, `/about/`, `/contact/`, `/posts/category/builds/`, `/posts/search/?q=Project`, `/accounts/register/step1/`, `/accounts/login/` y `/accounts/password_reset/`.

Advertencia confirmada durante arranque y tests: `staticfiles/` no existe.

## Inventario de comportamiento

| Área | Comportamiento observado |
| --- | --- |
| Landing, home, about y contacto GET | Renderizan correctamente. |
| Categoría, búsqueda y detalle de post | Renderizan con los datos del fixture. |
| Comentarios | Un anónimo es redirigido a login; un usuario autenticado puede crear un comentario. |
| Creación de posts | Anónimo: redirección a login. Usuario sin permiso: 403. Usuario con permiso: el render directo falla (ver errores). |
| Registro | El registro de dos pasos redirige a home y crea usuario/perfil, pero pierde `has_moto=True`. |
| Perfil | Requiere autenticación. |
| Password reset GET | Renderiza. El POST para una cuenta existente falla antes de enviar correo. |
| Contacto POST | Falla al intentar abrir el backend SMTP local no configurado. |

## Errores confirmados

1. **`Post.save()` no puede guardar un post existente.** Al llamar `save()` sobre un `Post` cuya URL/slug ya existe (incluido el propio registro), la condición `while Post.objects.filter(slug=self.slug).exists()` entra y usa `original_slug` sin haberlo inicializado. Resultado reproducible: `UnboundLocalError` con `original_slug`. Esto bloquea ediciones de posts.
2. **Crear post con permisos puede fallar al renderizar.** La plantilla base accede a `request.META.HTTP_REFERER`; una petición directa a `/posts/new/` sin ese encabezado termina con `VariableDoesNotExist` en lugar de mostrar el formulario.
3. **El registro pierde la selección positiva de motocicleta.** El flujo válido de registro persiste el perfil con `has_moto=False` aunque se envía `has_moto=True`.
4. **Contacto no es ejecutable localmente sin SMTP.** Un POST válido a `/contact/` termina en `ConnectionRefusedError: [WinError 10061]`; no hay configuración de correo local.
5. **Password reset no es funcional.** Un POST para el email existente falla con `NoReverseMatch`: falta la ruta nombrada `password_reset_confirm`, requerida por la plantilla de correo de Django.
6. **La autodetección de tests estaba rota.** Antes de añadir el marcador `apps/__init__.py`, `manage.py test` reportaba 0 tests, y etiquetas como `apps.core` provocaban un error de importación. El marcador se añadió exclusivamente para ejecutar las pruebas de caracterización.

## Pruebas de caracterización

Se añadieron nueve pruebas en `apps/core/tests.py`, `apps/accounts/tests.py` y `apps/posts/tests.py`. Cubren las rutas públicas, contacto, registro, autenticación de perfil, password reset GET, categorías, búsqueda, detalle, comentarios, permisos de posts y los fallos de `Post.save()` y del formulario de creación.

Ejecución final:

```text
python manage.py test -v 2
Ran 9 tests ... OK
```

Los tests fijan los defectos intencionalmente como comportamiento baseline; no constituyen correcciones.

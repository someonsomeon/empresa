# Aplicación de escritorio - Login + Recuperación + CRUD ↔ Excel

Instrucciones rápidas:

1. Crear entorno virtual e instalar dependencias:

   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt

2. Configurar envío de correo (opcional): editar `app/config.py` y completar los datos de SMTP.

3. Ejecutar la aplicación:

   python main.py

Notas:
- Por ahora el envío de correos está deshabilitado por defecto (modo de pruebas imprime el código en consola).
- Las contraseñas se almacenan hasheadas con bcrypt (via passlib).
- La base de datos de empleados se guarda en `app/data.xlsx`.
- Usuario admin por defecto: `admin` / `admin` (cámbiala tras iniciar sesión).

## Crear usuarios
Si necesitas crear más usuarios, usa el script:

    python app/create_user.py usuario correo@example.com

El script pedirá la contraseña (o usa --password). Esto añadirá al `app/users.json` el usuario con la contraseña hasheada y el email (necesario para recuperación).

## Configurar SMTP (opcional)
Edita `app/config.py` y ajusta:
- `SMTP_ENABLED = True`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
- `FROM_ADDRESS` (ej.: `ranimnasser1102@gmail.com`)

Ejemplo para Gmail (recomendado usar App Password):
```python
SMTP_ENABLED = True
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "tu_correo@gmail.com"
SMTP_PASSWORD = "tu_app_password"
FROM_ADDRESS = "ranimnasser1102@gmail.com"
```

El correo de recuperación usará el asunto **"Restaurar contraseña"** y en el cuerpo incluirá el código de 5 dígitos con instrucciones para copiar y pegar en la aplicación. En modo de desarrollo (cuando `SMTP_ENABLED = False`) el código se imprimirá en la consola en lugar de enviarse.


## Exportar y empaquetar
- Para exportar la base de datos a CSV: abre la aplicación y pulsa "Exportar CSV" (se guarda junto a `app/data.xlsx`).
- Para crear un ejecutable Windows usando PyInstaller:

    pip install pyinstaller
    pyinstaller --onefile --add-data "app/data.xlsx;app" --add-data "app/users.json;app" main.py

Esto creará `dist/main.exe` listo para distribuir.

## Pruebas rápidas (smoke test)
Hay un script de pruebas que realiza operaciones básicas de CRUD y verifica autenticación y generación de códigos:

    python app/smoke_test.py

Úsalo para validar que el entorno está bien configurado antes de usar la app.

## Notas sobre códigos de recuperación
- Los códigos generados son de 5 dígitos y caducan en 15 minutos por seguridad.
- Si el envío por SMTP está activo, el código se envía por correo desde `FROM_ADDRESS` con asunto **"Restaurar contraseña"**; si SMTP está deshabilitado, el código se imprime en la consola (modo desarrollo).
- Si el correo tarda, puedes usar el botón **Reenviar código** en la ventana de recuperación.
- Para depuración activa `SMTP_DEBUG=True` como variable de entorno para ver la conversación SMTP en consola.




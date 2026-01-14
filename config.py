# Configuración SMTP y opciones
# Por seguridad puedes usar variables de entorno en vez de guardar credenciales en el repo.
# Para activar SMTP pon SMTP_ENABLED = True y completa los datos o exporta las variables de entorno.
import os

SMTP_ENABLED = os.getenv("SMTP_ENABLED", "False") == "True"  # True/False
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "ranimnasser1102@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "yourpassword")
FROM_ADDRESS = os.getenv("FROM_ADDRESS", SMTP_USER or "ranimnasser1102@gmail.com")
# Nombre visible del remitente (opcional). Puedes dejar vacío para usar solo la dirección.
FROM_NAME = os.getenv("FROM_NAME", "AdminEmpleados")
SMTP_DEBUG = os.getenv("SMTP_DEBUG", "False") == "True"  # Enable smtplib debug output (True/False)
# Timeout (seconds) for SMTP socket connections
SMTP_TIMEOUT = int(os.getenv("SMTP_TIMEOUT", "10"))

# Theme colors (shared across GUI)
THEME_BG = '#2b2b33'          # main window background (dark)
THEME_PANEL = '#1f1f24'       # inner panels / entries background
THEME_TEXT = '#f5f5f5'        # main text color
THEME_MUTED = '#dcdcdc'       # secondary text / entry text
THEME_PLACEHOLDER = '#bdbdbd' # placeholder / subdued label
THEME_ACCENT = '#F8E3A9'      # accent (button) color
THEME_BORDER = '#3a3a43'      # thin border color

# Ejemplo para Gmail (editar o exportar variables de entorno):
# SMTP_ENABLED = True
# SMTP_HOST = "smtp.gmail.com"
# SMTP_PORT = 587
# SMTP_USER = "tu_correo@gmail.com"
# SMTP_PASSWORD = "tu_app_password"  # usa App Password de Google
# FROM_ADDRESS = "no-reply@tudominio.com"

# Archivos de datos
BASE_DIR = os.path.dirname(__file__)
DATA_EXCEL = os.path.join(BASE_DIR, "data.xlsx")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

# Nota: para exportar variables de entorno en PowerShell:
# $Env:SMTP_ENABLED = "True"
# $Env:SMTP_HOST = "smtp.gmail.com"
# $Env:SMTP_USER = "tu_correo@gmail.com"
# $Env:SMTP_PASSWORD = "tu_app_password"
# $Env:FROM_ADDRESS = "no-reply@tudominio.com"


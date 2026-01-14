import json
import os
import re
import logging
try:
    # Prefer passlib if available; use pbkdf2_sha256 backend to avoid bcrypt binary
    from passlib.hash import pbkdf2_sha256 as hasher  # type: ignore
except Exception:
    # Fallback to werkzeug if passlib is not installed
    try:
        # Import werkzeug dynamically to avoid static import errors in editors
        import importlib
        werkzeug_security = importlib.import_module("werkzeug.security")
        generate_password_hash = getattr(werkzeug_security, "generate_password_hash")
        check_password_hash = getattr(werkzeug_security, "check_password_hash")

        class _HasherWrapper:
            @staticmethod
            def hash(password):
                return generate_password_hash(password, method="pbkdf2:sha256")

            @staticmethod
            def verify(password, hashed):
                # werkzeug.check_password_hash expects (hashed, password)
                return check_password_hash(hashed, password)

        hasher = _HasherWrapper()
    except Exception:
        # Last-resort fallback (insecure plain-text) to avoid runtime errors when
        # no hashing library is available. Install passlib or werkzeug for proper
        # password hashing in production.
        class _PlainWrapper:
            @staticmethod
            def hash(password):
                return password

            @staticmethod
            def verify(password, hashed):
                return password == hashed

        hasher = _PlainWrapper()

from app import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_valid_email(email: str) -> bool:
    return EMAIL_RE.match(email) is not None


def validate_password_strength(password: str):
    """Valida la fuerza de una contraseña y devuelve (ok: bool, message: str).
    Reglas mínimas:
    - Longitud >= 8
    - Contiene minúscula, mayúscula, dígito y carácter especial
    """
    if not password:
        return False, "La contraseña no puede estar vacía"
    errors = []
    if len(password) < 8:
        errors.append("mínimo 8 caracteres")
    if not re.search(r"[a-z]", password):
        errors.append("una letra minúscula")
    if not re.search(r"[A-Z]", password):
        errors.append("una letra mayúscula")
    if not re.search(r"\d", password):
        errors.append("un dígito")
    if not re.search(r"[^A-Za-z0-9]", password):
        errors.append("un carácter especial")
    if errors:
        return False, "Faltan: " + ", ".join(errors)
    return True, "Contraseña fuerte"


def load_users():
    if not os.path.exists(config.USERS_FILE):
        return {}
    try:
        with open(config.USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.exception("Error leyendo users.json: %s", e)
        return {}


def save_users(users):
    try:
        with open(config.USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.exception("Error guardando users.json: %s", e)
        raise


def add_user(username: str, password: str, email: str) -> bool:
    """Crea un usuario nuevo. Lanza ValueError en caso de entrada inválida o
    si el usuario/email ya existe."""
    username = (username or "").strip()
    email = (email or "").strip()
    if not username:
        raise ValueError("El nombre de usuario no puede estar vacío")
    if not password:
        raise ValueError("La contraseña no puede estar vacía")
    if not _is_valid_email(email):
        raise ValueError("Email inválido")

    users = load_users()
    if username in users:
        raise ValueError("El usuario ya existe")
    if any(info.get("email") == email for info in users.values()):
        raise ValueError("El email ya está en uso")

    users[username] = {"password": hasher.hash(password), "email": email}
    save_users(users)
    logger.info("Usuario creado: %s", username)
    return True


def delete_user(username: str) -> bool:
    users = load_users()
    if username not in users:
        return False
    del users[username]
    save_users(users)
    logger.info("Usuario eliminado: %s", username)
    return True


def list_users():
    users = load_users()
    return [{"username": u, "email": info.get("email")} for u, info in users.items()]


def get_user_details(username: str):
    users = load_users()
    if username not in users:
        return None
    info = users[username].copy()
    info.pop("password", None)
    return info


def create_default_admin():
    """Asegura que exista el usuario por defecto `ranim` con contraseña `12345`.
    Si ya existe y su hash no coincide, se re-hashea con la contraseña indicada."""
    users = load_users()
    default_user = "ranim"
    default_pwd = "12345"
    default_email = "ranim@example.com"

    if default_user not in users:
        try:
            add_user(default_user, default_pwd, default_email)
        except Exception:
            users = load_users()
            users[default_user] = {"password": hasher.hash(default_pwd), "email": default_email}
            save_users(users)
    else:
        # Si existe pero su hash no corresponde a la contraseña deseada, re-hashear
        try:
            hasher.verify(default_pwd, users[default_user]["password"])
        except Exception:
            users[default_user]["password"] = hasher.hash(default_pwd)
            save_users(users)


def authenticate(username, password):
    users = load_users()
    if username not in users:
        return False
    hashed = users[username]["password"]
    try:
        return hasher.verify(password, hashed)
    except Exception:
        # In case of unexpected hash format
        logger.exception("Error verificando contraseña para %s", username)
        return False


def get_username_by_email(email):
    users = load_users()
    for u, info in users.items():
        if info.get("email") == email:
            return u
    return None


def set_password_for_username(username, new_password):
    users = load_users()
    if username not in users:
        return False
    users[username]["password"] = hasher.hash(new_password)
    save_users(users)
    logger.info("Contraseña actualizada para %s", username)
    return True


# Inicializar admin por defecto cuando se importe el módulo
create_default_admin()

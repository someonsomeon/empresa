import os
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from app import config
import logging

# Código temporal almacenado en memoria (email -> {code, ts, sent})
pending_codes = {}

# Logger para envíos de email
logger = logging.getLogger('email_utils')
logging.basicConfig(level=logging.INFO)


def generate_code():
    return f"{random.randint(0, 99999):05d}"


def _log_send(email_address, code, sent, attempts=None, exc=None):
    ts = datetime.utcnow().isoformat()
    logger.info("Email send: %s code=%s sent=%s attempts=%s exc=%s", email_address, code, sent, attempts, exc)
    try:
        log_path = os.path.join(config.BASE_DIR, 'email.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{ts} - {email_address} - {code} - sent={sent} - attempts={attempts} - exc={exc}\n")
    except Exception:
        logger.exception("No se pudo escribir en email.log")


def log_event(event_type: str, email_address: str = None, message: str = None):
    """Registra un evento arbitrario en el archivo de log principal (`email.log`).
    event_type: por ejemplo 'weak_password_attempt'
    """
    ts = datetime.utcnow().isoformat()
    logger.info("Event: %s email=%s message=%s", event_type, email_address, message)
    try:
        log_path = os.path.join(config.BASE_DIR, 'email.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{ts} - EVENT:{event_type} - email={email_address} - msg={message}\n")
    except Exception:
        logger.exception("No se pudo escribir evento en email.log")


def send_code(email_address):
    """Genera y envía un código. Devuelve (code, sent_bool)."""
    code = generate_code()
    ts = datetime.utcnow()
    # Guardamos información enriquecida
    pending_codes[email_address] = {"code": code, "ts": ts, "sent": False}

    subject = "Restaurar contraseña"

    text_body = (
        f"Hola,\n\nSe solicitó restaurar la contraseña de tu cuenta.\n\n"
        f"Tu código de recuperación es: {code}\n\n"
        "Copia y pega este código en la aplicación para restablecer tu contraseña.\n"
        "Si no solicitaste esto, ignora este mensaje.\n\n"
        "Saludos."
    )
    html_body = (
        f"<html><body><p>Hola,</p><p>Se solicitó restaurar la contraseña de tu cuenta.</p>"
        f"<p><b>Tu código de recuperación es: {code}</b></p>"
        "<p>Copia y pega este código en la aplicación para restablecer tu contraseña.</p>"
        "<p>Si no solicitaste esto, ignora este mensaje.</p><p>Saludos.</p></body></html>"
    )

    if config.SMTP_ENABLED:
        msg = EmailMessage()
        msg["Subject"] = subject
        # Si se proporcionó un nombre, formateamos "Nombre <correo>"
        if getattr(config, 'FROM_NAME', None):
            msg["From"] = f"{config.FROM_NAME} <{config.FROM_ADDRESS}>"
        else:
            msg["From"] = config.FROM_ADDRESS
        msg["To"] = email_address
        msg["X-Priority"] = "1"
        msg["Importance"] = "high"
        msg.set_content(text_body)
        msg.add_alternative(html_body, subtype='html')

        sent = False
        attempts = 0
        max_attempts = 3
        last_exception = None
        while attempts < max_attempts and not sent:
            attempts += 1
            try:
                # Use configured timeout to avoid blocking the main thread indefinitely
                timeout = getattr(config, 'SMTP_TIMEOUT', 10)
                with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=timeout) as server:
                    if getattr(config, 'SMTP_DEBUG', False):
                        server.set_debuglevel(1)
                    server.starttls()
                    server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                    server.send_message(msg)
                sent = True
                print(f"Código enviado por SMTP a {email_address} (From: {config.FROM_ADDRESS}, Subj: {subject}, attempt={attempts})")
            except Exception as e:
                last_exception = e
                print(f"Error enviando SMTP (attempt {attempts}):", e)
                try:
                    import traceback
                    traceback.print_exc()
                except Exception:
                    pass
                # Espera un momento antes de reintentar
                import time
                time.sleep(2) 

        pending_codes[email_address] = {"code": code, "ts": ts, "sent": sent, "attempts": attempts}
        _log_send(email_address, code, sent, attempts=attempts, exc=repr(last_exception) if last_exception else None)
        if not sent and last_exception:
            # Re-raise la última excepción para diagnóstico externo si es necesario
            raise last_exception
        return code, sent

    else:
        # Modo de desarrollo: imprimir el código en consola y el remitente
        from_addr = f"{config.FROM_NAME} <{config.FROM_ADDRESS}>" if getattr(config, 'FROM_NAME', None) else config.FROM_ADDRESS
        print(f"[DEV] From: {from_addr}")
        print(f"[DEV] Código para {email_address}: {code}")
        pending_codes[email_address] = {"code": code, "ts": ts, "sent": False}
        _log_send(email_address, code, False, attempts=0, exc=None)
        return code, False


def verify_code(email_address, code, expiry_minutes: int = 15):
    """Verifica que el código coincida y no esté caducado (por defecto 15 minutos)."""
    info = pending_codes.get(email_address)
    if not info:
        return False
    if str(info.get("code")) != str(code):
        return False
    ts = info.get("ts")
    if not ts:
        return False
    if datetime.utcnow() - ts > timedelta(minutes=expiry_minutes):
        # código caducado
        return False
    return True


# Nota: `verify_code` definida arriba con expiración; la definición simple sobrante fue eliminada

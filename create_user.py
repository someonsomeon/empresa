import argparse
import getpass
import json
import os
from passlib.hash import bcrypt
from app import config


def load_users():
    if not os.path.exists(config.USERS_FILE):
        return {}
    with open(config.USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(config.USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def main():
    p = argparse.ArgumentParser(description="Crear o actualizar usuario para la aplicación")
    p.add_argument("username", help="Nombre de usuario")
    p.add_argument("email", help="Correo electrónico del usuario")
    p.add_argument("--password", help="Contraseña (si no se provee se pedirá) ")
    args = p.parse_args()

    pwd = args.password
    if not pwd:
        pwd = getpass.getpass("Contraseña: ")
        pwd_confirm = getpass.getpass("Confirmar contraseña: ")
        if pwd != pwd_confirm:
            print("Las contraseñas no coinciden.")
            return

    users = load_users()
    users[args.username] = {"password": bcrypt.hash(pwd), "email": args.email}
    save_users(users)
    print(f"Usuario '{args.username}' creado/actualizado con email {args.email}.")


if __name__ == '__main__':
    main()

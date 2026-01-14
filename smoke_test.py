import os
import app.excel_db as excel_db
import app.auth as auth
import app.email_utils as email_utils
import app.config as config


def run():
    print("Asegurando archivo de datos...")
    excel_db.ensure_file()
    rows = excel_db.read_all()
    print(f"Filas iniciales: {len(rows)}")

    print("Agregando registro de prueba...")
    excel_db.add_record({"Nombre":"Test", "Cédula":"000", "Cargo":"QA", "Salario":"1000"})
    rows = excel_db.read_all()
    print(f"Filas tras agregar: {len(rows)}")

    print("Actualizando registro 0...")
    excel_db.update_record(0, {"Nombre":"Test2","Cédula":"111","Cargo":"Dev","Salario":"2000"})
    rows = excel_db.read_all()
    print("Fila 0:", rows[0])

    print("Eliminando registro 0...")
    excel_db.delete_record(0)
    rows = excel_db.read_all()
    print(f"Filas tras eliminar: {len(rows)}")

    print("Probando autenticación admin (admin/admin):", auth.authenticate("admin", "admin"))

    print("Probando generación de código de recuperación (modo dev) para admin@example.com")
    code = email_utils.send_code("admin@example.com")
    print("Código generado:", code)
    print("Verificación:", email_utils.verify_code("admin@example.com", code))

    print("Smoke test finalizado")

if __name__ == '__main__':
    run()

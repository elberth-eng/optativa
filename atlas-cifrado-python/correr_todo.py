"""Reinicia la práctica y corre todos los pasos, con pausa para tomar capturas."""
import os
import re
import subprocess
import sys
from pathlib import Path

from pymongo.errors import OperationFailure

from config import get_database

ENV_FILE = Path(".env")
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
STEPS = [
    "create_collection.py",
    "create_data_key.py",
    "insert_patient.py",
    "verify_encryption.py",
    "create_view.py",
    "read_public_view.py",
    "test_validation.py",
]


def child_env():
    return {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}


def reset_practice():
    db = get_database()
    for name in ("patients_public", "patients", "__keyVault"):
        db.drop_collection(name)


def save_data_key_id(data_key_id):
    text = ENV_FILE.read_bytes().decode("utf-8")
    new_text = re.sub(
        r"^DATA_KEY_ID=.*$",
        f'DATA_KEY_ID="{data_key_id}"',
        text,
        flags=re.M,
    )
    ENV_FILE.write_bytes(new_text.encode("utf-8"))
    # Los scripts heredan este entorno y load_dotenv no lo sobrescribe.
    os.environ["DATA_KEY_ID"] = data_key_id


def run_step(number, script):
    os.system("cls" if os.name == "nt" else "clear")
    print(f"===== Paso {number} de {len(STEPS)}: python {script} =====\n", flush=True)

    if script == "create_data_key.py":
        result = subprocess.run(
            [sys.executable, script],
            env=child_env(),
            capture_output=True,
            encoding="utf-8",
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            return False
        data_key_id = re.search(UUID_PATTERN, result.stdout, re.M).group(0)
        save_data_key_id(data_key_id)
        return True

    return subprocess.run([sys.executable, script], env=child_env()).returncode == 0


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    print("Esto borra patients, patients_public y __keyVault, y los crea de nuevo.")
    if input("Escribe SI para continuar: ").strip() != "SI":
        print("Cancelado. No se borró nada.")
        return

    try:
        reset_practice()
    except OperationFailure:
        print("\nSin permiso para borrar: dale Atlas admin a tu usuario y repite.")
        return

    for number, script in enumerate(STEPS, start=1):
        if not run_step(number, script):
            print(f"\nFalló {script}. Se detuvo la práctica.")
            return
        input("\nToma tu captura y presiona Enter para continuar...")

    os.system("cls" if os.name == "nt" else "clear")
    print("Listo: se corrieron todos los pasos.")


if __name__ == "__main__":
    main()

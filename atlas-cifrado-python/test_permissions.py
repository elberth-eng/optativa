"""Comprueba los permisos del usuario público. Córrelo sin el rol Atlas admin."""
from datetime import datetime, timezone

from pymongo.errors import OperationFailure

from config import get_database


def attempt(label, action):
    try:
        print(f"PERMITIDO | {label} | {action()}")
    except OperationFailure as error:
        print(f"DENEGADO  | {label} | código {error.code}")


def main():
    db = get_database()
    attempt("leer patients_public", lambda: db["patients_public"].count_documents({}))
    attempt("leer patients", lambda: db["patients"].find_one({}, {"_id": 1}))
    attempt("leer __keyVault", lambda: db["__keyVault"].find_one({}, {"_id": 1}))
    attempt(
        "escribir en patients",
        lambda: db["patients"].insert_one({
            "full_name": "Prueba",
            "created_at": datetime.now(timezone.utc),
        }).inserted_id,
    )
    attempt(
        "escribir en patients_public",
        lambda: db["patients_public"].insert_one({"x": 1}).inserted_id,
    )


if __name__ == "__main__":
    main()

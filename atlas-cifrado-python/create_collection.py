from config import get_database


def main():
    db = get_database()

    db.create_collection(
        "patients",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "full_name", "email", "national_id",
                    "diagnosis", "created_at",
                ],
                "properties": {
                    "full_name": {
                        "bsonType": "string",
                        "minLength": 3,
                        "maxLength": 120,
                    },
                    "email": {
                        "bsonType": "string",
                        "pattern": r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                    },
                    "national_id": {
                        "bsonType": "binData",
                        "description": "Debe llegar cifrado como BinData",
                    },
                    "diagnosis": {
                        "bsonType": "binData",
                        "description": "Debe llegar cifrado como BinData",
                    },
                    "age": {
                        "bsonType": "int",
                        "minimum": 0,
                        "maximum": 120,
                    },
                    "created_at": {
                        "bsonType": "date",
                    },
                },
            }
        },
        validationLevel="strict",
        validationAction="error",
    )

    print("Colección 'patients' creada con validación JSON Schema.")


if __name__ == "__main__":
    main()

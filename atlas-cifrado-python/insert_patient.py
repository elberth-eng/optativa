import os
import uuid
from datetime import datetime, timezone

from bson.binary import Binary
from bson.codec_options import CodecOptions, UuidRepresentation
from pymongo.encryption import Algorithm, ClientEncryption

from config import DB_NAME, get_client

KEY_VAULT_NAMESPACE = f"{DB_NAME}.__keyVault"


def main():
    client = get_client()
    db = client[DB_NAME]

    data_key_id = Binary.from_uuid(uuid.UUID(os.getenv("DATA_KEY_ID")))

    with open("master-key.bin", "rb") as key_file:
        master_key = key_file.read()

    client_encryption = ClientEncryption(
        kms_providers={"local": {"key": master_key}},
        key_vault_namespace=KEY_VAULT_NAMESPACE,
        key_vault_client=client,
        codec_options=CodecOptions(
            uuid_representation=UuidRepresentation.STANDARD
        ),
    )

    encrypted_national_id = client_encryption.encrypt(
        "CURP-123456HDFRRS09",
        key_id=data_key_id,
        algorithm=Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic,
    )

    encrypted_diagnosis = client_encryption.encrypt(
        "Hipertensión controlada",
        key_id=data_key_id,
        algorithm=Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random,
    )

    patient = {
        "full_name": "Ana López",
        "email": "ana.lopez@example.com",
        "age": 34,
        "national_id": encrypted_national_id,
        "diagnosis": encrypted_diagnosis,
        "created_at": datetime.now(timezone.utc),
    }

    result = db["patients"].insert_one(patient)
    print("Paciente guardado con ID:", result.inserted_id)

    client_encryption.close()
    client.close()


if __name__ == "__main__":
    main()

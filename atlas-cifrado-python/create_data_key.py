from bson.codec_options import CodecOptions, UuidRepresentation
from pymongo.encryption import ClientEncryption

from config import DB_NAME, get_client

KEY_VAULT_COLLECTION = "__keyVault"
KEY_VAULT_NAMESPACE = f"{DB_NAME}.{KEY_VAULT_COLLECTION}"


def main():
    client = get_client()

    # Evita dos llaves con el mismo nombre si el script se ejecuta otra vez.
    client[DB_NAME][KEY_VAULT_COLLECTION].create_index(
        "keyAltNames",
        unique=True,
        partialFilterExpression={"keyAltNames": {"$exists": True}},
    )

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

    data_key_id = client_encryption.create_data_key(
        "local",
        key_alt_names=["patients-data-key"],
    )

    print("Guarda este DATA_KEY_ID en .env:")
    print(data_key_id.as_uuid())

    client_encryption.close()
    client.close()


if __name__ == "__main__":
    main()

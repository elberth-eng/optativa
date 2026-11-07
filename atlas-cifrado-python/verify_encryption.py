from config import get_database


def main():
    db = get_database()
    patient = db["patients"].find_one({"full_name": "Ana López"})
    print(patient)


if __name__ == "__main__":
    main()

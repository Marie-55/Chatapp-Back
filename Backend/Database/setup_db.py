from local_db import ChatDatabase

if __name__ == "__main__":
    db_creator = ChatDatabase()
    db_creator.create_tables()
    db_creator.close()
    print("Database tables created successfully.")

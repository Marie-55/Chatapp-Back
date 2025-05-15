import sqlite3
from datetime import datetime

import sqlite3
from datetime import datetime

class ChatDatabase:
    def __init__(self, db_name='chat_app.db'):
        """Initialize the database connection"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._enable_foreign_keys()
    
    def _enable_foreign_keys(self):
        """Enable foreign key constraints in SQLite"""
        self.cursor.execute("PRAGMA foreign_keys = ON")
    
    def create_tables(self):
        """Create all tables with their relationships"""
        self._create_users_table()
        self._create_chatroom_table()
        self._create_message_table()
        self._create_users_chatrooms_table()
        self.conn.commit()
    
    def _create_users_table(self):
        """Create the Users table with Argon2id hashed passwords"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,  -- Argon2id hash
            public_key TEXT NOT NULL,
            encrypted_private_key TEXT NOT NULL,
            status BOOLEAN DEFAULT FALSE,  -- FALSE=logout, TRUE=login
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
    
    def _create_chatroom_table(self):
        """Create the Chatroom table with optional password"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Chatroom (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hashed_password TEXT,  -- NULL for public chatrooms
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES Users(id)
        )
        ''')
    
    def _create_message_table(self):
        """Create the Message table with encryption fields"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,  -- chatroom_id
            ciphertext TEXT NOT NULL,
            z_pub TEXT NOT NULL,  -- sender's public key
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES Users(id),
            FOREIGN KEY (receiver_id) REFERENCES Chatroom(id)
        )
        ''')
    
    def _create_users_chatrooms_table(self):
        """Create the junction table for many-to-many relationship"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users_Chatrooms (
            chatroom_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (chatroom_id, user_id),
            FOREIGN KEY (chatroom_id) REFERENCES Chatroom(id),
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
        ''')
    
    def close(self):
        """Close the database connection"""
        self.conn.close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":
    with ChatDatabase() as db:
        db.create_tables()
        print("Chat application database tables created successfully.")
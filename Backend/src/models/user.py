from datetime import datetime
from Database.init import db
from sqlalchemy import *

# creating the user as a database modle (sqlalchemy model)
class User(db.Model):
    __tablename__ = 'users'

    user_id  = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  # Argon2id hash?
    public_key = Column(String(512), nullable=False)
    encrypted_private_key = Column(String(1024), nullable=False)
    status = Column(String(10), default='logout') 
    created_at = Column(DateTime, default=datetime.utcnow)
    # login_attempts = Column(Integer, default=0)
    # last_attempt = Column(DateTime)
    
    # Relationships
    created_chatrooms = db.relationship('Chatroom', backref='creator', lazy=True)
    messages = db.relationship('Message', backref='sender', lazy=True)
    chatrooms = db.relationship('UserChatroom', back_populates='user')

    def __repr__(self):
        return f'<User {self.username}>'
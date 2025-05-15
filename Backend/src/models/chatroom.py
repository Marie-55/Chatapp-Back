from datetime import datetime
from Database.init import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

class Chatroom(db.Model):
    __tablename__ = 'chatrooms'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    hashed_password = Column(String(255))  # Optional, for private chatrooms
    created_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = db.relationship('Message', backref='chatroom', lazy=True)
    members = db.relationship('UserChatroom', back_populates='chatroom')
    def __repr__(self):
        return f'<Chatroom {self.name}>'
from datetime import datetime
from Database.init import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

class Message(db.Model):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True,name='message_id')
    sender_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('chatrooms.id'), nullable=False, name='receiver')
    ciphertext = Column(String(2048), nullable=False)
    z_pub = Column(String(512), nullable=False , name='sender_pub')  # sender public key
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id}>'
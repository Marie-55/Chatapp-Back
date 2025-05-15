from Database.init import db
from sqlalchemy import Column, Integer, ForeignKey

class UserChatroom(db.Model):
    __tablename__ = 'users_chatrooms'

    chatroom_id = Column(Integer, ForeignKey('chatrooms.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)

    # Relationships
    user = db.relationship('User', back_populates='chatrooms')
    chatroom = db.relationship('Chatroom', back_populates='members')

    def __repr__(self):
        return f'<UserChatroom user:{self.user_id} chatroom:{self.chatroom_id}>'
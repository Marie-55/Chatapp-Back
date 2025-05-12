import hashlib
import secrets
from datetime import datetime

from flask import jsonify
from sqlalchemy import UUID
from Database.init import db
from ..models.chatroom import Chatroom
from ..models.user_chatroom import UserChatroom
from ..models.message import Message

from ..models.user import User
from passlib.hash import argon2

from flask import session

class ChatroomService:
    @staticmethod
    def create_chatroom(name, password, user_id):
        try:            
            # Hash pw again with Argon2id  for storage
            final_hash = argon2.using(type='ID').hash(password)
            
            # Create and store the chatroom
            new_chatroom = Chatroom(
                name=name,
                hashed_password=final_hash,
                created_by=user_id
            )
            db.session.add(new_chatroom)
            # get the ID of the new chatroom
            db.session.flush()  
            
            # Add the creator as a member
            membership = UserChatroom(
                chatroom_id=new_chatroom.id,
                user_id=user_id
            )
            db.session.add(membership)
            db.session.commit()
            
            return new_chatroom, 201

        except Exception as e:
            db.session.rollback()
            return str(e), 500
    
    @staticmethod
    def join_chatroom(chatroomName, password, user_id):
        print(f"session user: {session['user_id']}")
        try:
            print(f"session user: {session['user_id']}")
            chatroom = Chatroom.query.filter(
                Chatroom.name == chatroomName).first()            
            if not chatroom:
                return {"success": False, "error": "Chatroom not found"} , 400
            
            # Verify the password using Argon2id
            if not argon2.verify(password, chatroom.hashed_password):
                return {"success": False, "error": "Incorrect password"} , 200
            
            # Check if user is already a member
            existing_membership = UserChatroom.query.filter_by(
                chatroom_id=chatroom.id,
                user_id=user_id
            ).first()
            
            if existing_membership:
                return {"success": False, "error": "Already a member of this chatroom"} , 200
            
            # Add user to chatroom
            membership = UserChatroom(
                chatroom_id=chatroom.id,
                user_id=user_id
            )
            db.session.add(membership)
            db.session.commit()
            
            return {"success": True} , 200
        except Exception as e:
            db.session.rollback()
            return str(e) , 500
    
    @staticmethod
    def leave_chatroom(chatroom_id, user_id):
        try:
            membership = UserChatroom.query.filter_by(
                chatroom_id=chatroom_id,
                user_id=user_id
            ).first()
            
            if not membership:
                return  f"Not a member of this chatroom" ,401
            
            db.session.delete(membership)
            
            # Check if this was the last user in the chatroom
            remaining_members = UserChatroom.query.filter_by(
                chatroom_id=chatroom_id
            ).count()
            
            # If no users left, delete the chatroom
            if remaining_members == 0:
                chatroom = Chatroom.query.get(chatroom_id)
                db.session.delete(chatroom)
            
            db.session.commit()
            return {"success": True} , 200
        except Exception as e:
            db.session.rollback()
            return str(e) ,500
    @staticmethod
    def get_chatroom_users(chatroom_id, requesting_user_id):
        try:
            # Verify if the  user is a member
            membership = UserChatroom.query.filter_by(
                chatroom_id=chatroom_id,
                user_id=requesting_user_id
            ).first()
            
            if not membership:
                return {"success": False, "error": "Not authorized to view this chatroom since this user is not a member of this chatroom"}
            
            # get all users in the chatroom
            users = db.session.query(User).join(
                UserChatroom, User.user_id == UserChatroom.user_id
            ).filter(
                UserChatroom.chatroom_id == chatroom_id
            ).all()
            
            user_list = [{
                "id": user.user_id,
                "username": user.username,
                "status": user.status,
            } for user in users]
            
            return {"success": True, "users": user_list}
        except Exception as e:
            return {"success": False, "error": str(e)}
    @staticmethod
    def kick_user_from_chatroom(chatroom_id, current_user_id, kicked_user_id):
        try:
            # Verify if the user is a the owner of the chatroom
            chatroom = Chatroom.query.get(chatroom_id)
            if not chatroom:
                return f"Chatroom not found" , 400
            if str(chatroom.created_by) != str(current_user_id):
                return f"Not authorized to kick users from this chatroom" ,401
            # Verify if the user is a member
            membership = UserChatroom.query.filter_by(
                chatroom_id=chatroom_id,
                user_id=kicked_user_id
            ).first()
            
            if not membership:
                return f"This user is not a member of this chatroom" , 400
            
            db.session.delete(membership)
            
            db.session.commit()
            return {"success": True} , 200
        except Exception as e:
            db.session.rollback()
            return str(e) , 500
    @staticmethod
    def delete_chatroom(chatroom_id, user_id):
        try:
            # Get the chatroom - using proper query syntax
            chatroom = Chatroom.query.filter_by(id=chatroom_id).first()
            if not chatroom:
                return f"Chatroom not found", 404
            
            # Verify ownership
            if str(chatroom.created_by) != str(user_id):
                return f"Not authorized to delete this chatroom", 403
            
            # Delete related messages (using correct column names)
            
            UserChatroom.query.filter_by(chatroom_id=chatroom_id).delete()
            
            # Delete chatroom itself
            db.session.delete(chatroom)
            db.session.commit()
            
            return {"success": True, "message": "Chatroom deleted successfully"}, 200
        
        except Exception as e:
            db.session.rollback()
            return str(e), 500
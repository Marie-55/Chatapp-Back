from src.models.user import User
from Database.init import db
from datetime import datetime
from argon2 import PasswordHasher



class UserController:
    @staticmethod
    def create_user(username, hashed_password, public_key, encrypted_private_key):
        """Create a new user"""
        new_user = User(
            username=username,
            hashed_password=hashed_password,
            public_key=public_key,
            encrypted_private_key=encrypted_private_key
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(usr):
        """Get user by username"""
        user=User.query.filter_by(username=usr).first()
        print(user)
        return user

    @staticmethod
    def update_user_status(user_id, status):
        """Update user login status"""
        user = User.query.get(user_id)
        if user:
            user.status = status
            db.session.commit()
        return user

    @staticmethod
    def increment_login_attempts(username):
        """Increment failed login attempts"""
        user = User.query.filter_by(username=username).first()
        if user:
            user.login_attempts += 1
            user.last_attempt = datetime.utcnow()
            db.session.commit()
        return user

    @staticmethod
    def reset_login_attempts(username):
        """Reset login attempts after successful login"""
        user = User.query.filter_by(username=username).first()
        if user:
            user.login_attempts = 0
            db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_public_key(public_key):
        """Get user by public key"""
        return User.query.filter_by(public_key=public_key).first()
    @staticmethod
    def get_user_by_encrypted_private_key(encrypted_private_key):
        """Get user by encrypted private key"""
        return User.query.filter_by(encrypted_private_key=encrypted_private_key).first()
    @staticmethod
    def update_user_keys(username, public_key, encrypted_private_key):
        """Update user keys"""
        user = UserController.get_user_by_username(username)
        if not user:
            raise ValueError("User not found")
        if user:
            user.public_key = public_key
            user.encrypted_private_key = encrypted_private_key
            db.session.commit()
        return user
    @staticmethod
    def delete_user(user_id):
        """Delete a user"""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
        return user
    
    @staticmethod
    def get_user_password(username):
        """Get user password"""
        user = UserController.get_user_by_username(username)
        if not user:
            raise ValueError("User not found")
        return user.hashed_password
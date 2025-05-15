from src.models.user import User
from Database.init import db
from datetime import datetime, timedelta
from src.utils.Back_password_hash import ph
from src.controllers.user_controller import UserController
from flask import jsonify, request, make_response,g
import jwt
import os
from dotenv import load_dotenv
from src.utils.model_to_dict import model_to_dict
from functools import wraps


load_dotenv('var.env')

class AuthService:
    @staticmethod
    def register_user(username, password, public_key, encrypted_private_key):

        """Register a new user"""
        if not username or not password or not public_key or not encrypted_private_key:
            if not username: print("username is required")
            if not password: print("password is required")
            if not public_key: print("publickey is required")
            if not encrypted_private_key: print("private key is required")
            raise ValueError("All fields are required")
        
        
        if UserController.get_user_by_username(username):
            raise ValueError("Username already exists")
        
        try:
            hashed_password = ph.hash(password)
            #create the new user 
            new_user = User(
                username=username,
                hashed_password=hashed_password,
                public_key=public_key,
                encrypted_private_key=encrypted_private_key
            )
            try:
                 # add user to the database

                db.session.add(new_user)
                db.session.commit()

            except Exception as e:
                db.session.rollback()
                raise Exception(f"Database error: {str(e)}")

            return new_user
        
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")
        

    @staticmethod
    def login(username, password, public_key=None, encrypted_private_key=None):
        '''"""Login a user"""'''
        print(f"user:{username}, password: {password}")
        if not username or not password:
            raise ValueError("Username and password are required")
        
        user= AuthService.authenticate_user(username,password)
        print("past auth")
        if not user:
            raise ValueError("User not found")
        try:
            
            # Reset login attempts on successful login
            if encrypted_private_key and public_key:
                UserController.update_user_keys(username, public_key, encrypted_private_key)
            #UserController.reset_login_attempts(username=username)
            UserController.update_user_status(user.user_id, status='login') #creating a user session
            db.session.commit()
            # 2. Generate token if successful
            access,refresh = AuthService.generate_tokens(username)

            
            return {
            "access_token": access,
            "refresh_token": refresh,
            "public_key": public_key,
            "user": model_to_dict(user)
        }
        
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error during login: {str(e)}")

    @staticmethod
    def authenticate_user(username, password):
        """Authenticate a user with username and password"""
        print("trying to authenticate the user")
        if not username or not password:
            raise ValueError("Username and password are required")
        user = UserController.get_user_by_username(username)
        if not user:
            raise ValueError("User not found")
        try:
            ph.verify(UserController.get_user_password(username), password)
            return user
        except Exception as e:
            UserController.increment_login_attempts(username)
            raise Exception(f"Authentication failed: {str(e)}")#
        
    @staticmethod
    def generate_access_token(username):
        """Generate a 30-minute access token"""
        if not username:
            raise ValueError("User not found")
        user = UserController.get_user_by_username(username)
        user_id=user.user_id
        access_token = jwt.encode(
            {
                "user_id": str(user_id),
                "username": str(username),
                "public_key": str(user.public_key),
                "exp": datetime.utcnow() + timedelta(minutes=30),
                "type": "access"
            },
            os.getenv("SECRET_KEY"),
            algorithm="HS256"
        )
        print(f"Access token: {access_token}")
        return access_token

    @staticmethod
    def generate_refresh_token(username):
        """Generate a 7-day refresh token"""
        if not username:
            raise ValueError("User not found")
        user = UserController.get_user_by_username(username)
        user_id=user.user_id
        refresh_token = jwt.encode(
            {
                "user_id": str(user_id),
                "username": str(username),
                "public_key": str(user.public_key),
                "exp": datetime.utcnow() + timedelta(days=7),
                "type": "refresh"
            },
            os.getenv("SECRET_KEY"),
            algorithm="HS256"
        )

        print(f"refresh token: {refresh_token}")
        return refresh_token
    
    @staticmethod
    def generate_tokens(username):
        '''generate authentication tokens for a usr'''
        user=UserController.get_user_by_username(username)
        if not user:
            raise ValueError("User not found")
        try:
            #create access tokens
            access_token=AuthService.generate_access_token(str(username))
            #create refresh token
            
            refresh_token = AuthService.generate_refresh_token(str(username))
            return access_token, refresh_token
        except Exception as e:
            raise Exception(f"Error generating tokens: {str(e)}")
        
    
    @staticmethod
    def refresh_tokens(refresh_token):
        """Generate new tokens using a refresh token"""
        try:
            # Verify refresh token
            payload = jwt.decode(
                refresh_token,
                os.getenv("SECRET_KEY"),
                algorithms=["HS256"]
            )
            
            if payload["type"] != "refresh":
                raise ValueError("Not a refresh token")

            # Generate new tokens
            new_access = AuthService.generate_access_token(payload["username"])
            new_refresh = AuthService.generate_refresh_token(payload["username"])
            
            return {
                "access_token": new_access,
                "refresh_token": new_refresh
            }
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token expired")
        except Exception as e:
            raise ValueError(f"Invalid token: {str(e)}")
    @staticmethod
    def verify_token(token):
        if not token:
            raise ValueError("Token is required")
        try:
            # Decode the token using the secret key
            decoded_token = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            return decoded_token
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired!")  # Raise instead of returning a response
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token!")     # Raise instead of returning a response
        except Exception as e:
            raise ValueError(f"Error verifying token: {str(e)}")
        
    @staticmethod
    def logout(username):
        user=UserController.get_user_by_username(username)
        if not user:
            raise ValueError("User not found")
        try:
        # For now, we'll just update the user's status
            UserController.update_user_status(username, status=False)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Logout failed: {str(e)}")
            return False
    

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            token_type, token = auth_header.split()
            if token_type != 'Bearer':
                raise ValueError("Invalid token type")
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            current_user = data["user_id"]
            
        except Exception as e:
            return jsonify({'error': str(e)}), 401

        return f(current_user,*args, **kwargs)
    return decorated
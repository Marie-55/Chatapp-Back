# backend/app.py
from flask import Flask, jsonify
from Database.init import init_db
import os
from dotenv import load_dotenv
from src.routes.auth import auth_routes
from src.routes.chatroom import chatroom_bp
from flask_cors import CORS
from flask import Blueprint


# Load environment variables from var.env
load_dotenv('var.env')
app_routes = Blueprint('home', __name__)

@app_routes.route('/')
def home():
    return "Backend is live! "

def create_app():
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app, origins=["https://chatapp-back-97m4.onrender.com"])
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Secret key for JWT
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    # Initialize the SQLAlchemy database
    init_db(app)
    
    # Register blueprints (routes)
    app.register_blueprint(auth_routes, url_prefix='/api/auth')
    app.register_blueprint(chatroom_bp, url_prefix='/api/chatroom')
    app.register_blueprint(app_routes, url_prefix='/api/')

    
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Default port is 5000
    port = int(os.getenv('PORT', 10000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
# backend/app.py
from flask import Flask, jsonify, render_template_string
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

# @app_routes.route('/')
# def home():
#     return "Backend is live! "



@app_routes.route('/')
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Backend Status</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin-top: 100px;
                    background-color: #f0f2f5;
                }
                h1 {
                    color: #2c3e50;
                }
                .status {
                    font-size: 24px;
                    color: #27ae60;
                    margin: 20px;
                }
            </style>
        </head>
        <body>
            <h1>Flask Backend</h1>
            <div class="status"> Backend is live!</div>
            <p>Try these endpoints:</p>
            <ul style="list-style: none; padding: 0;">
                <li><a href="/api/auth">/api/auth</a></li>
                <li><a href="/api/chatroom">/api/chatroom</a></li>
            </ul>
        </body>
        </html>
    ''')

def create_app():
    app = Flask(__name__)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
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

from flask import Blueprint, make_response,g
import src.services.auth_service as auth
from flask import request, jsonify
from flask_limiter import Limiter
from src.utils.model_to_dict import model_to_dict
import jwt


auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        user = auth.AuthService.register_user(
            data.get('username'),
            data.get('password'),
            data.get('publicKey'),
            data.get('encrypted_private_key')
        )
        result = auth.AuthService.login(
            data.get('username'),
            data.get('password')
        )

        response = make_response(jsonify({
            "message": "Login successful",
            "token": result['access_token'],  # Make sure this matches what frontend expects
            "encrypted_private_key": result['user'].get('encrypted_private_key'),  # Add this line
            "public_key": result['public_key'],  
            "tokens": {
                "access_token": result['access_token'],
                "refresh_token": result['refresh_token'],
                "user": result['user']
            }
        }),200)

        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # usr=model_to_dict(user)
    # return jsonify({"message": "User created", "user": usr}), 201

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
            
        result = auth.AuthService.login(
            data.get('username'),
            data.get('password')
        )
        g.current_user = result['user'] 
        # Create response
        response = make_response(jsonify({
            "message": "Login successful",
            "token": result['access_token'],  # Make sure this matches what frontend expects
            "encrypted_private_key": result['user'].get('encrypted_private_key'),  # Add this line
            "public_key": result['public_key'],  
            "tokens": {
                "access_token": result['access_token'],
                "refresh_token": result['refresh_token'],
                "user": result['user']
            }
        }),200)
       
                    
        
        # Set refresh token as secure cookie
        response.set_cookie(
            'refresh_token',
            result["refresh_token"],
            httponly=True,
            secure=False,  # Enable in production
            max_age=604800,  # 7 days
            samesite='Strict'
        )

        return response
    except Exception as e:
        return jsonify({"error in login route": str(e)}), 500   
    


@auth_routes.route('/refresh_token', methods=['POST'])
def refresh_token():
    """Get new access token using refresh token"""
    refresh_token = request.cookies.get('refresh_token')
    
    if not refresh_token:
        return jsonify({"error": "Refresh token missing"}), 401
    
    try:
        new_tokens = auth.AuthService.refresh_tokens(refresh_token)
        
        response = make_response(jsonify({
            "access_token": new_tokens["access_token"],
            "expires_in": 1800
        }))
        
        # Optionally renew the refresh token
        response.set_cookie(
            'refresh_token',
            new_tokens["refresh_token"],
            httponly=True,
            secure=True,
            max_age=604800,
            samesite='Strict'
        )
        
        return response
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

@auth_routes.route('/validate_token', methods=['POST'])
def validate_token():
    """Validate access token"""
    token = request.cookies.get('refresh_token')
    try:
        payload = auth.AuthService.verify_token(token)
        return jsonify({"valid": True, "user": payload['username']}),200
    except ValueError as e:  # Catch raised ValueError messages
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    
@auth_routes.route('/logout', methods=['POST'])
def logout():
    """Invalidate user session"""
    try:
        auth.AuthService.logout(request.json.get('username'))
        return jsonify({"message": "Logged out successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@auth_routes.route('/protected-route',methods=['GET'])
@auth.token_required
def protected_route():
    data = g.data
    return jsonify({
        "message": f"Welcome ",
        "data": data  # or whatever you stored in the token
    })

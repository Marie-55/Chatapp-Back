from flask import Blueprint, g, json, request, jsonify, session
from ..services.chatroom_service import ChatroomService
import jwt 

class ChatroomController:
    @staticmethod
    def create_chatroom(user_id):
        data = request.get_json()

        if not data or 'chatroom_name' not in data or 'passcode' not in data:
            return jsonify({"success": False, "error": "Chatroom name and passcode are required"}), 400

        
        #user_id = "15929b81-65e5-4b6d-a1c4-771810a90625"
        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400
        name = data["chatroom_name"]
        password = data["passcode"]
        result, status = ChatroomService.create_chatroom(name, password, user_id)
       
        if status == 201:
                return jsonify({
                    "success": True, 
                    "chatroom": {
                        "id": result.id,
                        "name": result.name,
                        "created_by": result.created_by,
                        "created_at": result.created_at
                    }
                }), status
        else:
            return jsonify({"success": False, "error": str(result)}), status
    @staticmethod
    def join_chatroom():
        data = request.get_json()

        if not data or 'chatroomName' not in data or 'passcode' not in data:
            return jsonify({"success": False, "error": "Chatroom name and password are required"}), 400
        #user_id= "1b4d57ee-e692-490b-94db-adae44dae4b1"
        user_id = session.get("current_user")
        if not user_id: 
            return jsonify({"success": False, "error": "User ID is required"}), 400
        chatroomName = data["chatroomName"]
        passcode = data["passcode"]

        result ,status= ChatroomService.join_chatroom(chatroomName, passcode, user_id)
        if status == 200:
                return jsonify({
                    "success": True, 
                    "message": "joined successfully"
                }), status
        else:
            return jsonify({"success": False, "error": result}), status

    @staticmethod
    def leave_chatroom(chatroom_id):
        
        #user_id = "1b4d57ee-e692-490b-94db-adae44dae4b1"
        user_id = session.get("current_user")
        if not user_id: 
            return jsonify({"success": False, "error": "User ID is required"}), 400
        result, status = ChatroomService.leave_chatroom(chatroom_id, user_id)
        if status == 200:
            return jsonify({
                "success": True, 
                "message": "Left chatroom successfully"
            }), status
        else:
            return jsonify({"success": False, "error": result}), status
        
    @staticmethod
    def get_chatroom_users(chatroom_id):

        if not chatroom_id:
            return jsonify({"success": False, "error": "Chatroom ID is required"}), 400

        # Placeholder: you should replace this with actual user ID from auth
        user_id = session.get("current_user")
        #user_id = "15929b81-65e5-4b6d-a1c4-771810a90625"
        if not user_id: 
            return jsonify({"success": False, "error": "User ID is required"}), 400
        result = ChatroomService.get_chatroom_users(chatroom_id, user_id)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    @staticmethod
    def kick_user_from_chatroom(chatroom_id):
        data = request.get_json()
        kicked_user_id = data.get('user_id')
        current_user_id = session.get("current_user")
        #current_user_id = "15929b81-65e5-4b6d-a1c4-771810a90625"
        if not chatroom_id:
            return jsonify({"success": False, "error": "Chatroom ID is required"}), 400
        if not kicked_user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400


        result, status  = ChatroomService.kick_user_from_chatroom(chatroom_id, current_user_id,kicked_user_id)

        if status == 200:
            return jsonify({
                "success": True, 
                "message": "User kicked successfully"
            }), status
        else:
            return jsonify({"success": False, "error": result}), status
    @staticmethod
    def delete_chatroom(chatroom_id):

        if not chatroom_id:
            return jsonify({"success": False, "error": "Chatroom ID is required"}), 400

        # Placeholder: you should replace this with actual user ID from auth
        user_id = session.get("current_user")
        #user_id = "15929b81-65e5-4b6d-a1c4-771810a90625"
        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400
        result,status = ChatroomService.delete_chatroom(chatroom_id, user_id)
       
        if status == 201:
                return jsonify({
                    "success": True, 
                    "message": "Chatroom deleted successfully"
                }), status
        else:
            return jsonify({"success": False, "error": result}), status
        
    @staticmethod
    def check_chatroom_name():
        data = request.get_json()

        if not data or 'chatroomName' not in data:
            return jsonify({"success": False, "error": "Name is required"}), 400

        name = data["chatroomName"]
        result, status = ChatroomService.check_chatroom_name(name)
       
        if status == 200:
                return jsonify({
                    "success": True, 
                    "message": "Chatroom name is available"
                }), status
        else:
            return jsonify({"success": False, "error": result}), status

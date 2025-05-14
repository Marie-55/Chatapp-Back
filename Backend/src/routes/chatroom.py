from flask import Blueprint
from ..controllers.chatroom_controller import ChatroomController
from src.services.auth_service import token_required
chatroom_bp = Blueprint('chatroom', __name__)

# Define routes and connect them to controller methods
@chatroom_bp.route('/create', methods=['POST'])
@token_required
def create_chatroom(current_user ):
    user_id = current_user
    return ChatroomController.create_chatroom(user_id)

@chatroom_bp.route('/join', methods=['POST','OPTIONS'])
@token_required
def join_chatroom(current_user):
    user_id = current_user
    return ChatroomController.join_chatroom(user_id)

@chatroom_bp.route('/<chatroom_id>/leave', methods=['POST'])
@token_required
def leave_chatroom(chatroom_id,current_user):
    user_id = current_user
    return ChatroomController.leave_chatroom(chatroom_id,user_id)

@chatroom_bp.route('/<chatroom_id>/users', methods=['GET'])
@token_required
def get_chatroom_users(chatroom_id,current_user):
    user_id = current_user
    return ChatroomController.get_chatroom_users(chatroom_id,user_id)
@chatroom_bp.route('/<chatroom_id>/kick_user', methods=['POST'])
@token_required
def kick_user_from_chatroom(chatroom_id,current_user):
    user_id = current_user
    return ChatroomController.kick_user_from_chatroom(chatroom_id,user_id)

@chatroom_bp.route('/<chatroom_id>/delete', methods=['DELETE'])
@token_required
def delete_chatroom(chatroom_id,current_user):
    user_id = current_user
    return ChatroomController.delete_chatroom(chatroom_id,user_id)
@chatroom_bp.route('/check_name', methods=['POST'])
@token_required
def check_chatroom_name():
    return ChatroomController.check_chatroom_name()

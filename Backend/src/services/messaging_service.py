from flask_socketio import join_room, leave_room, emit
from datetime import datetime
from Database.init import db
from src.models.user import User
from src.models.chatroom import Chatroom
from src.models.message import Message
from src.models.user_chatroom import UserChatroom
from flask import Blueprint, request, jsonify
from src.models.chatroom import Chatroom
from src.models.message import Message
from uuid import UUID

message_bp = Blueprint('message', __name__)

@message_bp.route('/message', methods=['GET'])
def get_chatroom_messages():
    chatroom_id = request.args.get('chatroom_id')

    if not chatroom_id:
        return jsonify({'error': 'Chatroom name is required'}), 400

    # 1. Validate chatroom existence
    chatroom = Chatroom.query.get(chatroom_id)
    if not chatroom:
        return jsonify({'error': 'Chatroom not found'}), 404

    # 2. Get all messages in this chatroom, ordered by timestamp
    messages = Message.query \
        .filter_by(receiver_id=chatroom.id) \
        .order_by(Message.timestamp.asc()) \
        .all()

    # 3. Build JSON response
    messages_data = []
    for msg in messages:
        messages_data.append({
            'sender': msg.sender.username if msg.sender else 'Unknown',
            'encrypted_content': msg.ciphertext,
            'z_pub': msg.z_pub,
            'timestamp': msg.timestamp.isoformat()
        })

    return jsonify({'messages': messages_data}), 200


def register_message_handlers(socketio):
    @socketio.on('send_message')
    def handle_send_message(data):
        print("="*40)
        print(f"Received message data: {data}")
        print("="*40)

        try:
            sender_id = data.get('sender_id')
            chatroom_id = data.get('chatroom_id')
            encrypted_content = data.get('encrypted_content')
            sender_pub = data.get('z_pub')
            timestamp = datetime.utcnow()

            if not all([sender_id, chatroom_id, encrypted_content, sender_pub]):
                print("Missing one or more required fields.")
                socketio.emit('error', {'error': 'Missing required fields'})
                return

            sender = User.query.filter_by(user_id=sender_id).first()
            if not sender:
                print(f"Sender with ID {sender_id} not found.")
                socketio.emit('error', {'error': 'Invalid sender'})
                return
            print(f"Sender {sender.username} validated.")

            user_chatroom = UserChatroom.query.filter_by(user_id=sender.user_id, chatroom_id=chatroom_id).first()
            if not user_chatroom:
                print(f"Sender not part of chatroom {chatroom_id}")
                socketio.emit('error', {'error': 'Sender not part of chatroom'})
                return
            print(f"Sender is part of chatroom {chatroom_id}")

            receiver = UserChatroom.query.filter(
                UserChatroom.chatroom_id == chatroom_id,
                UserChatroom.user_id != sender_id
            ).first()

            if receiver:
                receiver_id = receiver.user_id
                print(f"Found receiver: {receiver_id}")
            else:
                receiver_id = None
                print("No specific receiver found (group chat or solo)")

            message = Message(
                sender_id=sender.user_id,
                receiver_id=receiver_id,
                ciphertext=encrypted_content,
                z_pub=sender_pub,
                timestamp=timestamp
            )
            db.session.add(message)

            try:
                db.session.commit()
                print(f"Message committed to DB with ID: {message}")
            except Exception as e:
                print(f"DB commit failed: {e}")
                import traceback
                traceback.print_exc()
                socketio.emit('error', {'error': 'Failed to save message to database'})
                return

            socketio.emit('receive_message', {
                'chatroom': chatroom_id,
                'sender': sender_id,
                'encrypted_content': encrypted_content,
                'sender_pub': sender_pub,
                'timestamp': timestamp.isoformat()
            }, room=chatroom_id, include_self=True)

            print(f"Broadcasted message to chatroom {chatroom_id}")

        except Exception as e:
            import traceback
            print("Exception during send_message:")
            traceback.print_exc()
            socketio.emit('error', {'error': 'Internal server error'})

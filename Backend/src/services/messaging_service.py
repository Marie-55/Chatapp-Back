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
        print(f"Received message data: {data}")

        try:
            sender_id = data.get('sender_id')  # UUID for the sender
            chatroom_id = data.get('chatroom_id')  # UUID for the chatroom
            encrypted_content = data.get('encrypted_content')
            sender_pub = data.get('z_pub')  # Assuming 'sender_pub' corresponds to sender's public key
            timestamp = datetime.utcnow()

            # Step 1: Validate sender
            sender = User.query.filter_by(user_id=sender_id).first()
            if not sender:
                socketio.emit('error', {'error': 'Invalid sender'})
                return

            # Step 2: Validate chatroom (check if sender is part of the chatroom)
            user_chatroom = UserChatroom.query.filter_by(user_id=sender.user_id, chatroom_id=chatroom_id).first()
            if not user_chatroom:
                socketio.emit('error', {'error': 'Sender not part of chatroom'})
                return

            # Step 3: Save message
            message = Message(
                sender_id=sender.user_id,
                receiver_id=user_chatroom.chatroom_id,  # Use chatroom_id from UserChatroom
                ciphertext=encrypted_content,
                z_pub=sender_pub,  # sender's public key
                timestamp=timestamp
            )
            db.session.add(message)

            # Commit to the database and check if successful
            try:
                db.session.commit()
                print(f"Saved encrypted message from {sender.username} in chatroom {chatroom_id}")
            except Exception as e:
                print(f"Error committing to database: {e}")
                socketio.emit('error', {'error': 'Failed to save message to database'})
                return

            # Step 4: Broadcast to chatroom
            print(f"Attempting to broadcast message to chatroom {chatroom_id}")
            socketio.emit('receive_message', {
                'chatroom': chatroom_id,
                'sender': sender_id,
                'encrypted_content': encrypted_content,
                'sender_pub': sender_pub,
                'timestamp': timestamp.isoformat()
            }, room=chatroom_id, include_self=False)

            print(f"Broadcasted message to chatroom {chatroom_id}")

        except Exception as e:
            print("Error handling message:", str(e))
            socketio.emit('error', {'error': 'Internal server error'})

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Forum, Message, Profile
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.forum_id = self.scope['url_route']['kwargs']['forum_id']
        self.room_group_name = f'chat_{self.forum_id}'
        self.user = self.scope["user"]

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Set user as online
        await self.set_user_online(True)
        
        # Notify others that user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.user.username,
                'status': 'online'
            }
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Set user as offline
        await self.set_user_online(False)
        
        # Notify others that user is offline
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.user.username,
                'status': 'offline'
            }
        )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        # Save message to database
        await self.save_message(username, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'type': 'message'
        }))

    async def user_status(self, event):
        # Send user status to WebSocket
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'status': event['status'],
            'type': 'status'
        }))

    @database_sync_to_async
    def set_user_online(self, status):
        Profile.objects.filter(user=self.user).update(is_online=status)

    @database_sync_to_async
    def save_message(self, username, message):
        user = User.objects.get(username=username)
        forum = Forum.objects.get(id=self.forum_id)
        Message.objects.create(
            sender=user,
            forum=forum,
            content=message
        )

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_user = int(self.scope['url_route']['kwargs']['user_id'])
        
        self.room_group_name = f'private_chat_{min(self.user.id, self.other_user)}_{max(self.user.id, self.other_user)}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']

        # Save message to database
        await self.save_message(sender_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'private_message',
                'message': message,
                'sender_id': sender_id
            }
        )

    async def private_message(self, event):
        message = event['message']
        sender_id = event['sender_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'type': 'private_message'
        }))

    @database_sync_to_async
    def save_message(self, sender_id, message):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=self.other_user)
        Message.objects.create(
            sender=sender,
            recipient=receiver,
            content=message,
            is_private=True
        ) 
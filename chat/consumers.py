import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_name = None
        self.chat_group_name = None

    async def connect(self):
        self.chat_name = self.scope['url_route']['kwargs']['chat_name']
        self.chat_group_name = self.chat_name

        # Join chat group
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave chat group
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            message = data.get('message')
            username = data.get('username')
            mark_read = data.get('mark_read', False)
            message_id = data.get('message_id')

            if message:
                # Save the message to the database
                chat = await self.get_chat(self.chat_name)
                sender = await self.get_profile(username)
                message_obj = await self.save_message(chat, sender, message)

                # Send message to chat group
                await self.channel_layer.group_send(
                    self.chat_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': username,
                        'message_id': message_obj.id
                    }
                )

            if mark_read and message_id:
                # Mark specific message as read
                await self.mark_message_as_read(message_id)

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        message_id = event['message_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'message_id': message_id
        }))

    @database_sync_to_async
    def get_chat(self, chat_name):
        pk = int(chat_name.replace('chat_', ''))
        return Chat.objects.get(pk=pk)

    @database_sync_to_async
    def get_profile(self, username):
        return User.objects.get(username=username).profile

    @database_sync_to_async
    def save_message(self, chat, sender, content):
        return Message.objects.create(chat=chat, sender=sender, content=content)

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            message.read = True
            message.save()
        except Message.DoesNotExist:
            pass

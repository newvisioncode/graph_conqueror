import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from castle_graph.models import Gif


def get_gif_or_none(pk):
    try:
        return Gif.objects.get(pk=pk)
    except Gif.DoesNotExist:
        return None


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self):
        super().__init__()
        self.global_group_name = "global"

    async def connect(self):
        user = self.scope["user"]
        if user and user.is_authenticated and user.contestuser and user.contestuser.is_active:
            await self.channel_layer.group_add(
                self.global_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        type_message = data.get('type', None)
        message = data.get('message', None)

        if type_message == 'gif' and isinstance(message, dict) and isinstance(message.get('gif', None), int):
            gif = await database_sync_to_async(get_gif_or_none)(message.get('gif'))
            if gif:
                message = {
                    'gif': gif.gif,
                    'group': self.scope['contest_group'].name,
                }
                await self.channel_layer.group_send(
                    self.global_group_name,
                    {
                        'type': 'gif',
                        'message': message
                    }
                )

    async def gif(self, event):
        await self.send(text_data=json.dumps({
            "type": "gif",
            "message": event["message"]
        }))


    async def capture_castle(self, event):
        await self.send(text_data=json.dumps({
            "type": "capture_castle",
            "message": event["message"]
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.global_group_name,
            self.channel_name
        )

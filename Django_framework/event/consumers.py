# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EventUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "event_updates",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "event_updates",
            self.channel_name
        )

    async def event_updated(self, event):
        message = event['message']
        event_id = event['event_id']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'event_id': event_id
        }))

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EventUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(self.scope['query_string'])
        self.user_id = self.scope['query_string'].decode().split('=')[1]  # Extract user_id from query string
        print("user_id:", self.user_id)
        self.room_name = f'user_{self.user_id}'
        
        # Add the user's websocket connection to a group based on user_id
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        
        await self.accept()
        print(f"WebSocket connected for user_id: {self.user_id}")

    async def disconnect(self, close_code):
        # Remove the user's websocket connection from the group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
        print(f"WebSocket disconnected for user_id: {self.user_id}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("Data received:", text_data_json)
        """
        message = text_data_json.get('message')

        if message == 'update_event':
            event_id = text_data_json.get('event_id')
            # Notify users involved in the event
            await self.notify_users_involved(event_id)
        """
    async def notify_users_involved(self,involved_user_ids, event_id):
        # Determine users involved in the event (replace this with your logic)
        involved_user_ids = ['user1', 'user2', 'user3']  # Example: Replace with actual logic

        for user_id in involved_user_ids:
            room_name = f'user_{user_id}'
            message = {
                'type': 'event_notification',
                'message': f'Event {event_id} has been updated.'
            }
            await self.channel_layer.group_send(room_name, message)

    async def event_notification(self, event):
        message = event['message']
        # Send message to the websocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

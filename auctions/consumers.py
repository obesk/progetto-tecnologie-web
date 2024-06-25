import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BidConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.artwork_id = self.scope['url_route']['kwargs']['artwork_id']
		self.group_name = f'artwork_{self.artwork_id}'

		await self.channel_layer.group_add(
			self.group_name,
			self.channel_name
		)

		await self.accept()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			self.group_name,
			self.channel_name
		)

	async def receive(self, text_data):
		data = json.loads(text_data)
		message = data['message']

		await self.channel_layer.group_send(
			self.group_name,
			{
				'type': 'send_message',
				'message': message
			}
		)

	async def send_message(self, event):
		message = event['message']

		await self.send(text_data=json.dumps({
			'message': message
		}))

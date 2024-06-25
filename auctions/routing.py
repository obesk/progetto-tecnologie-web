from django.urls import path
from .consumers import BidConsumer

websocket_urlpatterns = [
	path('ws/bids/<int:artwork_id>/', BidConsumer.as_asgi()),
]
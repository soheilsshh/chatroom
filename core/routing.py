from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<forum_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/private/(?P<user_id>\d+)/$', consumers.PrivateChatConsumer.as_asgi()),
] 
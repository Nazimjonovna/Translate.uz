from django.urls import path, re_path
from .consumers import ChatConsumer


websocket_urlpatterns = [
    path('chat/', ChatConsumer.as_asgi())
    # re_path(r'^chat/(?P<chat_id>\w+)/$', ChatConsumer.as_asgi()),
    # re_path(r"^chat/$", ChatConsumer.as_asgi()),
]
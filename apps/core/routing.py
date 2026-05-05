from django.urls import re_path
from apps.core import consumers

websocket_urlpatterns = [
    re_path(r'ws/notificaciones/$', consumers.NotificationConsumer.as_asgi()),
]

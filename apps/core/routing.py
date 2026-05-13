from django.urls import re_path
from apps.core import consumers
from apps.asistente import consumers as asistente_consumers

websocket_urlpatterns = [
    re_path(r'ws/notificaciones/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/asistente/chat/$', asistente_consumers.AsistenteConsumer.as_asgi()),
]

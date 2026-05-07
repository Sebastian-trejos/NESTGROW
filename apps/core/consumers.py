import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if user and user.is_authenticated:
            self.group_name = f'usuario_{user.pk}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def nivel_subido(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'nivel_subido',
            'nivel': event['nivel'],
        }))

    async def huesos_ganados(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'huesos_ganados',
            'cantidad': event['cantidad'],
        }))

    async def taller_disponible(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'taller_disponible',
            'taller_id': event['taller_id'],
            'titulo': event['titulo'],
        }))

    async def seccion_desbloqueada(self, event):
        await self.send(text_data=json.dumps({
            'tipo':           'seccion_desbloqueada',
            'seccion_titulo': event['seccion_titulo'],
            'seccion_emoji':  event['seccion_emoji'],
            'seccion_pk':     event['seccion_pk'],
        }))

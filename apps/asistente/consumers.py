import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from .services import AsistenteMilo

logger = logging.getLogger(__name__)


class AsistenteConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated or user.role != 'profesor':
            await self.close()
            return
        self.profesor = user
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or '{}')
        except json.JSONDecodeError:
            await self._error('Mensaje inválido.')
            return

        mensaje = (data.get('mensaje') or '').strip()
        if not mensaje:
            await self._error('El mensaje no puede estar vacío.')
            return

        await self.send(json.dumps({'tipo': 'pensando'}))

        try:
            milo = AsistenteMilo()
            resultado = await milo.chat_planeacion(self.profesor, mensaje)
            await self.send(json.dumps({
                'tipo': 'respuesta',
                'texto': resultado['texto'],
                'motor': resultado['motor'],
            }))
        except Exception as exc:
            logger.exception('Error en AsistenteConsumer.receive: %s', exc)
            await self._error('Ocurrió un error. Intenta de nuevo.')

    async def _error(self, msg: str):
        await self.send(json.dumps({'tipo': 'error', 'texto': msg}))

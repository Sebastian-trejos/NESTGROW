import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from .services import AsistenteMilo

logger = logging.getLogger(__name__)


class AsistenteConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        try:
            user = self.scope.get('user')
            logger.warning(
                'AsistenteWS connect: user=%s auth=%s role=%s',
                getattr(user, 'username', None),
                getattr(user, 'is_authenticated', False),
                getattr(user, 'role', '?'),
            )

            if not user or not user.is_authenticated or getattr(user, 'role', '') != 'profesor':
                logger.warning('AsistenteWS: acceso denegado')
                await self.close(code=4003)
                return

            self.profesor = user
            await self.accept()
            logger.warning('AsistenteWS: %s aceptado', user.username)

        except Exception as exc:
            logger.exception('AsistenteWS connect EXCEPCION: %s', exc)
            try:
                await self.close(code=4000)
            except Exception:
                pass

    async def disconnect(self, code):
        logger.warning('AsistenteWS: desconectado code=%s', code)

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
            logger.exception('AsistenteWS receive error: %s', exc)
            await self._error('Ocurrió un error procesando tu mensaje. Intenta de nuevo.')

    async def _error(self, msg: str):
        await self.send(json.dumps({'tipo': 'error', 'texto': msg}))

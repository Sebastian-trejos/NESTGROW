from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Taller, SesionTaller


def _send_to_user(channel_layer, user_id, payload):
    async_to_sync(channel_layer.group_send)(f'usuario_{user_id}', payload)


@receiver(post_save, sender=Taller)
def notificar_taller_publicado(sender, instance, **kwargs):
    """Notifica a los estudiantes del salón cuando el profesor publica un taller."""
    update_fields = kwargs.get('update_fields')

    # Solo reaccionar cuando se guarda explícitamente el campo is_active
    if not update_fields or 'is_active' not in update_fields:
        return

    if not instance.is_active or not instance.salon:
        return

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    payload = {
        'type': 'taller_disponible',
        'taller_id': instance.pk,
        'titulo': instance.titulo,
    }

    for perfil in instance.salon.estudiantes.select_related('user').all():
        _send_to_user(channel_layer, perfil.user_id, payload)


@receiver(post_save, sender=SesionTaller)
def notificar_huesos_taller(sender, instance, **kwargs):
    """Envía notificación de huesos ganados cuando se completa una sesión."""
    update_fields = kwargs.get('update_fields')

    # Solo reaccionar cuando se guarda explícitamente el campo completada
    if not update_fields or 'completada' not in update_fields:
        return

    if not instance.completada or instance.huesos_ganados <= 0:
        return

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    _send_to_user(channel_layer, instance.estudiante_id, {
        'type': 'huesos_ganados',
        'cantidad': instance.huesos_ganados,
    })

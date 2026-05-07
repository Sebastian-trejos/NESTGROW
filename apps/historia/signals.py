"""
Historia mode signals.

Signal 1 — SeccionDesbloqueada post_save:
  Notifies every student in the salon via WebSocket when a professor
  unlocks a new section for their class.

Signal 2 — ProgresoLeccion post_save:
  Keeps EstudianteProfile.total_estrellas_historia in sync when a lesson
  progress record is modified outside the view (e.g. from the Django admin).
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SeccionDesbloqueada, ProgresoLeccion


@receiver(post_save, sender=SeccionDesbloqueada)
def on_seccion_desbloqueada(sender, instance, created, **kwargs):
    """Send a WebSocket notification to all students in the salon."""
    if not created:
        return

    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
    except ImportError:
        return

    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    salon   = instance.salon
    seccion = instance.seccion

    from apps.accounts.models import EstudianteProfile
    estudiantes = (
        EstudianteProfile.objects
        .filter(salon=salon)
        .values_list('user_id', flat=True)
    )

    payload = {
        'type':           'seccion_desbloqueada',
        'seccion_titulo': seccion.titulo,
        'seccion_emoji':  seccion.icono_emoji,
        'seccion_pk':     seccion.pk,
    }

    send = async_to_sync(channel_layer.group_send)
    for user_id in estudiantes:
        try:
            send(f'usuario_{user_id}', payload)
        except Exception:
            pass


@receiver(post_save, sender=ProgresoLeccion)
def on_progreso_completado(sender, instance, **kwargs):
    """
    Backup sync for total_estrellas_historia.
    The view already updates this field directly; this signal catches
    admin edits so the counter never drifts out of sync.
    """
    if not instance.completada:
        return

    try:
        from django.db.models import Sum
        from apps.accounts.models import EstudianteProfile

        total = (
            ProgresoLeccion.objects
            .filter(estudiante=instance.estudiante, completada=True)
            .aggregate(s=Sum('estrellas'))['s'] or 0
        )
        EstudianteProfile.objects.filter(
            user=instance.estudiante
        ).update(total_estrellas_historia=total)
    except Exception:
        pass

from django.db import models
from django.conf import settings


class MensajeChat(models.Model):
    ROL_CHOICES = [('user', 'Usuario'), ('assistant', 'Asistente')]
    MODO_CHOICES = [('planeacion', 'Planeación'), ('analisis', 'Análisis')]
    MOTOR_CHOICES = [('gemini', 'Gemini'), ('groq', 'Groq'), ('error', 'Error')]

    profesor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensajes_asistente',
    )
    rol = models.CharField(max_length=10, choices=ROL_CHOICES)
    contenido = models.TextField()
    modo = models.CharField(max_length=20, choices=MODO_CHOICES)
    motor_usado = models.CharField(max_length=10, choices=MOTOR_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Mensaje de Chat'
        verbose_name_plural = 'Mensajes de Chat'

    def __str__(self):
        return f'{self.profesor.username} [{self.rol}] — {self.created_at:%Y-%m-%d %H:%M}'

    @classmethod
    def limpiar_historial_anterior(cls, profesor, modo, mantener=20):
        """Elimina mensajes viejos dejando solo los últimos `mantener`."""
        ids = (
            cls.objects.filter(profesor=profesor, modo=modo)
            .order_by('-created_at')
            .values_list('id', flat=True)[mantener:]
        )
        cls.objects.filter(id__in=list(ids)).delete()

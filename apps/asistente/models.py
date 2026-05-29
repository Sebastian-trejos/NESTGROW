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


class PromptTemplate(models.Model):
    """System prompt editable desde el admin de Django, sin necesidad de redeploy."""
    NOMBRE_CHOICES = [
        ('planeacion',        'Asistente de Planeación (chat)'),
        ('correccion',        'Corrección de Milo (estudiante)'),
        ('generar_taller',    'Generador de Talleres con IA'),
        ('insights_periodo',  'Insights de Período (análisis)'),
    ]

    nombre = models.CharField(
        max_length=50,
        choices=NOMBRE_CHOICES,
        unique=True,
        verbose_name='Identificador del prompt',
    )
    system = models.TextField(verbose_name='System Prompt')
    activo = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1, verbose_name='Versión')
    updated_at = models.DateTimeField(auto_now=True)
    notas = models.TextField(
        blank=True,
        verbose_name='Notas internas',
        help_text='Descripción del propósito, cambios realizados, etc.',
    )

    class Meta:
        verbose_name = 'Prompt Template'
        verbose_name_plural = 'Prompt Templates'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.get_nombre_display()} v{self.version}'


class LlamadaIA(models.Model):
    """Registro de cada llamada real a la IA para métricas y observabilidad."""
    MOTOR_CHOICES = [
        ('gemini', 'Gemini'),
        ('groq', 'Groq'),
        ('cache', 'Cache (hit)'),
        ('sin_datos', 'Sin datos'),
        ('error', 'Error'),
    ]

    motor = models.CharField(max_length=10, choices=MOTOR_CHOICES)
    proposito = models.CharField(
        max_length=80, blank=True,
        help_text='Ej: chat_planeacion, milo_correccion, generar_taller',
    )
    latencia_ms = models.PositiveIntegerField(default=0, verbose_name='Latencia (ms)')
    exito = models.BooleanField(default=True)
    cache_hit = models.BooleanField(default=False, verbose_name='Respondido desde caché')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='llamadas_ia',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Llamada IA'
        verbose_name_plural = 'Llamadas IA'
        ordering = ['-created_at']

    def __str__(self):
        estado = '🎯 cache' if self.cache_hit else ('✅' if self.exito else '❌')
        return f'{estado} {self.motor} [{self.proposito}] — {self.created_at:%Y-%m-%d %H:%M}'

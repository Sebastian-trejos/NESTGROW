from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class SeccionHistoria(TimeStampedModel):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    icono_emoji = models.CharField(max_length=10, default='📖')
    color_hex = models.CharField(max_length=7, default='#6C63FF')
    is_desbloqueada_por_defecto = models.BooleanField(
        default=False,
        help_text='Si es True, todos los salones la ven desbloqueada sin acción del profesor.'
    )

    class Meta:
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
        ordering = ['orden']

    def __str__(self):
        return f"{self.icono_emoji} {self.titulo}"

    def get_total_lecciones(self):
        return self.lecciones.count()

    def get_lecciones_completadas_por(self, estudiante):
        return ProgresoLeccion.objects.filter(
            leccion__seccion=self,
            estudiante=estudiante,
            completada=True,
        ).count()


class SeccionDesbloqueada(TimeStampedModel):
    seccion = models.ForeignKey(
        SeccionHistoria, on_delete=models.CASCADE, related_name='desbloqueos'
    )
    salon = models.ForeignKey(
        'accounts.Salon', on_delete=models.CASCADE, related_name='secciones_desbloqueadas'
    )
    desbloqueada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='secciones_desbloqueadas_por_mi'
    )
    desbloqueada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seccion', 'salon')
        verbose_name = 'Sección Desbloqueada'
        verbose_name_plural = 'Secciones Desbloqueadas'

    def __str__(self):
        return f"{self.seccion} → {self.salon}"


class Leccion(TimeStampedModel):
    seccion = models.ForeignKey(
        SeccionHistoria, on_delete=models.CASCADE, related_name='lecciones'
    )
    titulo = models.CharField(max_length=200)
    descripcion_corta = models.CharField(max_length=200, blank=True)
    orden = models.PositiveIntegerField(default=0)
    puntos_xp = models.IntegerField(default=10)
    huesos_recompensa = models.IntegerField(default=3)
    tiempo_estimado_minutos = models.IntegerField(default=15)
    icono_emoji = models.CharField(max_length=10, default='📝')

    class Meta:
        verbose_name = 'Lección'
        verbose_name_plural = 'Lecciones'
        ordering = ['seccion__orden', 'orden']

    def __str__(self):
        return f"{self.icono_emoji} {self.titulo} ({self.seccion.titulo})"

    def get_total_actividades(self):
        return self.actividades.count()


class ActividadLeccion(TimeStampedModel):
    TIPOS = [
        ('introduccion', '🎬 Introducción'),
        ('vocabulario', '📚 Vocabulario'),
        ('listening', '🎧 Listening'),
        ('reading', '📖 Reading'),
        ('writing', '✏️ Writing'),
        ('minijuego_embed', '🎮 Minijuego'),
        ('dialogo', '💬 Diálogo'),
        ('pronunciacion', '🔊 Pronunciación'),
    ]

    leccion = models.ForeignKey(
        Leccion, on_delete=models.CASCADE, related_name='actividades'
    )
    orden = models.PositiveIntegerField(default=0)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    datos = models.JSONField(default=dict, help_text='Contenido prefabricado según el tipo de actividad')
    puntos_actividad = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['orden']

    def __str__(self):
        return f"{self.get_tipo_display()} (Lección: {self.leccion.titulo}, orden {self.orden})"

    def tiene_respuesta_correcta(self):
        return self.tipo in ('listening', 'reading', 'writing', 'pronunciacion', 'minijuego_embed')


class ProgresoLeccion(TimeStampedModel):
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progreso_lecciones'
    )
    leccion = models.ForeignKey(
        Leccion, on_delete=models.CASCADE, related_name='progresos'
    )
    completada = models.BooleanField(default=False)
    actividad_actual = models.PositiveIntegerField(default=0)
    puntos_obtenidos = models.IntegerField(default=0)
    estrellas = models.IntegerField(default=0)
    completada_en = models.DateTimeField(null=True, blank=True)
    intentos = models.IntegerField(default=0)

    class Meta:
        unique_together = ('estudiante', 'leccion')
        verbose_name = 'Progreso de Lección'
        verbose_name_plural = 'Progresos de Lección'

    def __str__(self):
        return f"{self.estudiante.username} → {self.leccion.titulo} ({self.estrellas}⭐)"

    def calcular_estrellas(self, total_actividades, respuestas_correctas):
        if total_actividades == 0:
            return 1
        pct = (respuestas_correctas / total_actividades) * 100
        if pct >= 90:
            return 3
        elif pct >= 70:
            return 2
        return 1


class RespuestaActividad(TimeStampedModel):
    progreso = models.ForeignKey(
        ProgresoLeccion, on_delete=models.CASCADE, related_name='respuestas'
    )
    actividad = models.ForeignKey(
        ActividadLeccion, on_delete=models.CASCADE, related_name='respuestas'
    )
    respuesta_dada = models.JSONField(default=dict)
    es_correcta = models.BooleanField(null=True, blank=True)
    respondida_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Respuesta de Actividad'
        verbose_name_plural = 'Respuestas de Actividad'
        ordering = ['respondida_en']

    def __str__(self):
        correcta = '✅' if self.es_correcta else ('❌' if self.es_correcta is False else '—')
        return f"{correcta} {self.actividad} por {self.progreso.estudiante.username}"

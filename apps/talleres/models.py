from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.accounts.models import Salon
from apps.games.models import Game


class Taller(TimeStampedModel):
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    profesor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='talleres_creados'
    )
    salon = models.ForeignKey(
        Salon, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='talleres', verbose_name='Salón'
    )
    puntos_xp = models.IntegerField(default=10, verbose_name='XP al completar')
    huesos_recompensa = models.IntegerField(default=5, verbose_name='Huesos al completar')
    is_active = models.BooleanField(default=False, verbose_name='Publicado')
    categorias_vocabulario = models.ManyToManyField(
        'content.Category',
        blank=True,
        related_name='talleres_asociados',
        verbose_name='Categorías de vocabulario',
        help_text='Palabras de estas categorías se desbloquearán al completar el taller',
    )

    class Meta:
        verbose_name = 'Taller'
        verbose_name_plural = 'Talleres'
        ordering = ['-created_at']

    def __str__(self):
        return self.titulo

    def get_bloques(self):
        return self.bloques.order_by('orden')

    def total_bloques(self):
        return self.bloques.count()

    def total_puntos_posibles(self):
        total = 0
        for b in self.bloques.filter(tipo='pregunta'):
            if hasattr(b, 'bloque_pregunta'):
                total += b.bloque_pregunta.puntaje_parcial
        return total


class BloqueTaller(TimeStampedModel):
    TIPO_CHOICES = [
        ('pregunta', '❓ Pregunta'),
        ('minijuego', '🎮 Minijuego'),
    ]
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE, related_name='bloques')
    orden = models.PositiveIntegerField(default=0)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    class Meta:
        verbose_name = 'Bloque de Taller'
        verbose_name_plural = 'Bloques de Taller'
        ordering = ['orden']

    def __str__(self):
        return f"Bloque {self.orden} ({self.get_tipo_display()}) — {self.taller.titulo}"

    def get_detalle(self):
        if self.tipo == 'minijuego':
            return getattr(self, 'bloque_minijuego', None)
        return getattr(self, 'bloque_pregunta', None)


class BloqueMinijuego(TimeStampedModel):
    bloque = models.OneToOneField(
        BloqueTaller, on_delete=models.CASCADE, related_name='bloque_minijuego'
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='bloques_taller')
    instruccion_extra = models.TextField(
        blank=True, verbose_name='Instrucción extra',
        help_text='Contexto adicional que el profesor puede dar al estudiante antes del juego.',
    )

    class Meta:
        verbose_name = 'Bloque Minijuego'
        verbose_name_plural = 'Bloques Minijuego'

    def __str__(self):
        return f"Minijuego: {self.game.title}"


class BloquePregunta(TimeStampedModel):
    TIPO_RESPUESTA = [
        ('opcion_multiple', '⭕ Opción múltiple (una correcta)'),
        ('casillas', '☑️ Casillas (varias correctas)'),
        ('parrafo', '✍️ Párrafo libre'),
    ]
    bloque = models.OneToOneField(
        BloqueTaller, on_delete=models.CASCADE, related_name='bloque_pregunta'
    )
    enunciado = models.TextField(verbose_name='Enunciado')
    tipo_respuesta = models.CharField(
        max_length=20, choices=TIPO_RESPUESTA, default='opcion_multiple',
        verbose_name='Tipo de respuesta'
    )
    imagen = models.ImageField(upload_to='talleres/preguntas/', blank=True, null=True)
    video_url = models.URLField(blank=True, verbose_name='URL de video (obsoleto)')
    video_archivo = models.FileField(
        upload_to='talleres/videos/', blank=True, null=True,
        verbose_name='Video (.mp4)'
    )
    puntaje_parcial = models.IntegerField(default=10, verbose_name='Puntos de esta pregunta')

    class Meta:
        verbose_name = 'Bloque Pregunta'
        verbose_name_plural = 'Bloques Pregunta'

    def __str__(self):
        return f"Pregunta: {self.enunciado[:60]}"

    @property
    def video_embed_url(self):
        url = self.video_url or ''
        if 'youtube.com/watch?v=' in url:
            vid = url.split('v=')[1].split('&')[0]
            return f'https://www.youtube-nocookie.com/embed/{vid}'
        if 'youtu.be/' in url:
            vid = url.split('youtu.be/')[1].split('?')[0]
            return f'https://www.youtube-nocookie.com/embed/{vid}'
        return url


class OpcionRespuesta(TimeStampedModel):
    pregunta = models.ForeignKey(
        BloquePregunta, on_delete=models.CASCADE, related_name='opciones'
    )
    texto = models.CharField(max_length=300, verbose_name='Texto de la opción')
    es_correcta = models.BooleanField(default=False, verbose_name='¿Es correcta?')

    class Meta:
        verbose_name = 'Opción de Respuesta'
        verbose_name_plural = 'Opciones de Respuesta'
        ordering = ['pk']

    def __str__(self):
        return f"{'✅' if self.es_correcta else '❌'} {self.texto}"


class RespuestaEstudiante(TimeStampedModel):
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='respuestas_taller'
    )
    pregunta = models.ForeignKey(
        BloquePregunta, on_delete=models.CASCADE, related_name='respuestas'
    )
    texto_respuesta = models.TextField(blank=True)
    opciones_elegidas = models.ManyToManyField(OpcionRespuesta, blank=True)
    es_correcta = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = 'Respuesta de Estudiante'
        verbose_name_plural = 'Respuestas de Estudiantes'
        unique_together = [('estudiante', 'pregunta')]

    def __str__(self):
        return f"{self.estudiante.username} → {self.pregunta}"


class SesionTaller(TimeStampedModel):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE, related_name='sesiones')
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sesiones_taller'
    )
    completada = models.BooleanField(default=False)
    revisado = models.BooleanField(default=False)  # True = vio resultado, desaparece del panel
    puntos_obtenidos = models.IntegerField(default=0)
    huesos_ganados = models.IntegerField(default=0)
    bloque_actual = models.IntegerField(default=0)
    completada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sesión de Taller'
        verbose_name_plural = 'Sesiones de Taller'
        unique_together = [('taller', 'estudiante')]

    def __str__(self):
        return f"{self.estudiante.username} — {self.taller.titulo}"


# ── Sistema de Periodos ────────────────────────────────────────────────────────

class Periodo(TimeStampedModel):
    """Ciclo de trabajo con fecha límite que el profesor asigna a un salón."""
    salon = models.ForeignKey(
        'accounts.Salon', on_delete=models.CASCADE, related_name='periodos',
        verbose_name='Salón',
    )
    titulo = models.CharField(max_length=120, verbose_name='Título',
                              help_text='Ej: Periodo 1 — Mayo 2026')
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin = models.DateField(verbose_name='Fecha límite')
    meta_historia = models.PositiveIntegerField(
        default=0, verbose_name='Meta de estrellas (Historia)',
        help_text='Número de estrellas de historia que el estudiante debe alcanzar. 0 = sin meta.',
    )
    is_activo = models.BooleanField(default=True, verbose_name='Activo')
    cerrado = models.BooleanField(default=False, verbose_name='Cerrado',
                                  help_text='Un período cerrado congela los resultados.')

    class Meta:
        verbose_name = 'Período'
        verbose_name_plural = 'Períodos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.titulo} ({self.salon})"

    @property
    def estado(self):
        from django.utils import timezone
        hoy = timezone.now().date()
        if self.cerrado:
            return 'cerrado'
        if hoy > self.fecha_fin:
            return 'vencido'
        if hoy < self.fecha_inicio:
            return 'futuro'
        return 'activo'


class AsignacionTaller(models.Model):
    """Relaciona un Taller con un Período."""
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE,
                                related_name='talleres_asignados')
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE,
                               related_name='asignaciones_periodo')
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Taller asignado'
        verbose_name_plural = 'Talleres asignados'
        unique_together = ('periodo', 'taller')
        ordering = ['orden']

    def __str__(self):
        return f"{self.periodo.titulo} → {self.taller.titulo}"


class AsignacionMinijuego(models.Model):
    """Relaciona un Game con un Período."""
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE,
                                related_name='minijuegos_asignados')
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='asignaciones_periodo')
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Minijuego asignado'
        verbose_name_plural = 'Minijuegos asignados'
        unique_together = ('periodo', 'game')
        ordering = ['orden']

    def __str__(self):
        return f"{self.periodo.titulo} → {self.game.title}"


class RegistroMinijuegoPeriodo(TimeStampedModel):
    """Rastrea si un estudiante completó un minijuego dentro de un período."""
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE,
                                related_name='registros_minijuego')
    asignacion = models.ForeignKey(AsignacionMinijuego, on_delete=models.CASCADE,
                                   related_name='registros')
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='registros_minijuego_periodo',
    )
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    completado = models.BooleanField(default=False)
    revisado = models.BooleanField(default=False)  # True = vio resultado, desaparece del panel

    class Meta:
        verbose_name = 'Registro de minijuego en período'
        verbose_name_plural = 'Registros de minijuegos en período'
        unique_together = ('asignacion', 'estudiante')

    def __str__(self):
        return f"{self.estudiante.username} — {self.asignacion.game.title} ({self.periodo.titulo})"

    @property
    def porcentaje(self):
        if self.max_score:
            return round((self.score / self.max_score) * 100)
        return 0

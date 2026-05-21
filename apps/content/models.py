from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel, ActiveModel


class Category(TimeStampedModel, ActiveModel):
    """Vocabulary category / topic (Animals, Colors, Numbers, etc.)"""
    name = models.CharField(max_length=100, verbose_name='Nombre (Español)')
    name_en = models.CharField(max_length=100, verbose_name='Nombre (Inglés)')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🐾')
    color = models.CharField(max_length=7, default='#6C63FF',
                             help_text='Color HEX para la tarjeta (ej: #FF6B6B)')
    order = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.icon} {self.name} / {self.name_en}"


class VocabularyItem(TimeStampedModel, ActiveModel):
    """A single vocabulary word with image and audio."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='vocabulary')
    word_es = models.CharField(max_length=100, verbose_name='Palabra en Español')
    word_en = models.CharField(max_length=100, verbose_name='Word in English')
    descripcion_es = models.TextField(blank=True, verbose_name='Descripción en español',
                                      help_text='Definición sencilla en español para el estudiante')
    pronunciacion_es = models.CharField(max_length=150, blank=True,
                                        verbose_name='Pronunciación aproximada',
                                        help_text='Ej: "dog" se pronuncia "dag"')
    image = models.ImageField(upload_to='vocabulary/images/', blank=True, null=True)
    audio = models.FileField(upload_to='vocabulary/audio/', blank=True, null=True,
                             help_text='Archivo .mp3 con la pronunciación en inglés')
    emoji = models.CharField(max_length=10, blank=True, default='',
                             verbose_name='Emoji representativo',
                             help_text='Emoji individual de la palabra (ej: 🐕 para Dog)')
    hint = models.CharField(max_length=200, blank=True,
                            verbose_name='Pista o contexto')
    difficulty = models.IntegerField(
        default=1, choices=[(1, 'Fácil'), (2, 'Medio'), (3, 'Difícil')]
    )
    is_unlocked_by_default = models.BooleanField(
        default=False, verbose_name='Desbloqueada por defecto',
        help_text='True = visible para todos los estudiantes sin completar nada'
    )
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden dentro de categoría')

    class Meta:
        verbose_name = 'Vocabulario'
        verbose_name_plural = 'Vocabulario'
        ordering = ['orden', 'word_en']

    def __str__(self):
        return f"{self.word_en} / {self.word_es} ({self.category.name})"


class VocabularioDesbloqueado(models.Model):
    """Registro de qué palabras ha desbloqueado cada estudiante."""
    FUENTE_CHOICES = [
        ('inicial', 'Inicial'),
        ('taller', 'Taller'),
        ('minijuego', 'Minijuego'),
    ]
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='vocabulario_desbloqueado'
    )
    item = models.ForeignKey(
        VocabularyItem, on_delete=models.CASCADE,
        related_name='desbloqueado_por'
    )
    desbloqueado_en = models.DateTimeField(auto_now_add=True)
    fuente = models.CharField(max_length=20, choices=FUENTE_CHOICES, default='inicial')

    class Meta:
        verbose_name = 'Vocabulario Desbloqueado'
        verbose_name_plural = 'Vocabulario Desbloqueado'
        unique_together = [('estudiante', 'item')]
        ordering = ['-desbloqueado_en']

    def __str__(self):
        return f"{self.estudiante.username} → {self.item.word_en}"


class HitoVocabulario(models.Model):
    """Hito de vocabulario desbloqueado — otorga huesos al alcanzar N palabras."""
    HITOS = [(10, 2), (25, 5), (50, 10), (100, 20), (200, 40)]

    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='hitos_vocabulario'
    )
    palabras_cantidad = models.IntegerField(verbose_name='Palabras al alcanzar el hito')
    huesos_ganados = models.IntegerField(verbose_name='Huesos otorgados')
    entregado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Hito de Vocabulario'
        verbose_name_plural = 'Hitos de Vocabulario'
        unique_together = [('estudiante', 'palabras_cantidad')]
        ordering = ['palabras_cantidad']

    def __str__(self):
        return f"{self.estudiante.username} — {self.palabras_cantidad} palabras → {self.huesos_ganados} 🦴"

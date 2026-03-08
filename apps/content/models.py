from django.db import models
from apps.core.models import TimeStampedModel, ActiveModel


class Category(TimeStampedModel, ActiveModel):
    """Vocabulary category / topic (Animals, Colors, Numbers, etc.)"""
    ICON_CHOICES = [
        ('🐾', 'Animales'), ('🎨', 'Colores'), ('🔢', 'Números'),
        ('🍎', 'Frutas'), ('🏠', 'Casa'), ('🏫', 'Escuela'),
        ('👗', 'Ropa'), ('🌦️', 'Clima'), ('👨‍👩‍👧', 'Familia'),
        ('🚗', 'Transporte'), ('🌿', 'Naturaleza'), ('🍔', 'Comida'),
    ]
    name = models.CharField(max_length=100, verbose_name='Nombre (Español)')
    name_en = models.CharField(max_length=100, verbose_name='Nombre (Inglés)')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, choices=ICON_CHOICES, default='🐾')
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
    image = models.ImageField(upload_to='vocabulary/images/', blank=True, null=True)
    audio = models.FileField(upload_to='vocabulary/audio/', blank=True, null=True,
                             help_text='Archivo .mp3 con la pronunciación en inglés')
    hint = models.CharField(max_length=200, blank=True,
                            verbose_name='Pista o contexto')
    difficulty = models.IntegerField(
        default=1, choices=[(1, 'Fácil'), (2, 'Medio'), (3, 'Difícil')]
    )

    class Meta:
        verbose_name = 'Vocabulario'
        verbose_name_plural = 'Vocabulario'
        ordering = ['word_en']

    def __str__(self):
        return f"{self.word_en} / {self.word_es} ({self.category.name})"

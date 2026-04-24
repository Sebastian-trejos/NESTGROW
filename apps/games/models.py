from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel, ActiveModel
from apps.content.models import Category


# ── Clasificación por puntaje ─────────────────────────────────────────────────
def clasificar_puntaje(pct):
    """Returns classification label based on score percentage."""
    if pct >= 90:
        return ('perfecto', '🏆 Perfecto', '#4CAF50')
    elif pct >= 70:
        return ('alto', '⭐ Alto', '#6C63FF')
    elif pct >= 50:
        return ('basico', '👍 Básico', '#FFB347')
    else:
        return ('bajo', '💪 Sigue practicando', '#FF6B6B')


def pct_to_nota(pct):
    """Convert percentage to Colombian 1-5 grade scale."""
    if pct >= 90:
        return 5.0
    elif pct >= 80:
        return 4.5
    elif pct >= 70:
        return 4.0
    elif pct >= 60:
        return 3.5
    elif pct >= 50:
        return 3.0
    elif pct >= 40:
        return 2.5
    else:
        return 2.0


class Game(TimeStampedModel, ActiveModel):
    GAME_TYPES = [
        ('drag_and_drop', '🖱️ Arrastra y Suelta'),
        ('word_search', '🔍 Sopa de Letras'),
        ('puzzle', '🧩 Rompecabezas'),
        ('audio_matching', '🎵 Juego de Audio'),
        ('painting', '🎨 Juego de Pintar'),
    ]
    DIFFICULTY = [
        (1, '⭐ Fácil'), (2, '⭐⭐ Medio'), (3, '⭐⭐⭐ Difícil')
    ]

    title = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    game_type = models.CharField(max_length=30, choices=GAME_TYPES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='games')
    difficulty = models.IntegerField(choices=DIFFICULTY, default=1)
    thumbnail = models.ImageField(upload_to='games/thumbnails/', blank=True, null=True)
    points_reward = models.IntegerField(default=5)
    time_limit = models.IntegerField(default=120, help_text='Tiempo en segundos (0 = sin límite)')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Juego'
        verbose_name_plural = 'Juegos'
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.get_game_type_display()} - {self.title}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('games:game_detail', kwargs={'pk': self.pk})


class UserProgress(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='player_progress')
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Progreso'
        verbose_name_plural = 'Progresos'
        unique_together = ('user', 'game')

    def percentage(self):
        if self.max_score == 0:
            return 0
        return int((self.score / self.max_score) * 100)

    def clasificacion(self):
        return clasificar_puntaje(self.percentage())

    def __str__(self):
        return f"{self.user} - {self.game} ({self.score} pts)"


class Score(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField()
    max_score = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)

    class Meta:
        ordering = ['-score', 'time_spent']

    def percentage(self):
        if self.max_score == 0:
            return 0
        return int((self.score / self.max_score) * 100)

    def clasificacion(self):
        return clasificar_puntaje(self.percentage())

    def __str__(self):
        return f"{self.user.username}: {self.score} en {self.game.title}"


# ── Logros / Medallas ─────────────────────────────────────────────────────────

class Logro(TimeStampedModel):
    """Badge/Achievement definition."""
    CATEGORIAS = [
        ('juegos', '🎮 Juegos'),
        ('puntaje', '⭐ Puntaje'),
        ('vocabulario', '📚 Vocabulario'),
        ('especial', '✨ Especial'),
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    icono = models.CharField(max_length=10, default='🏅')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='juegos')
    condicion_valor = models.IntegerField(default=1,
                                          help_text='Valor numérico para desbloquear (ej: 5 juegos)')
    color = models.CharField(max_length=7, default='#6C63FF')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Logro'
        verbose_name_plural = 'Logros'

    def __str__(self):
        return f"{self.icono} {self.nombre}"


class LogroUsuario(TimeStampedModel):
    """Junction: user has unlocked a badge."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='logros_obtenidos')
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE, related_name='usuarios')
    visto = models.BooleanField(default=False)  # False = show popup

    class Meta:
        unique_together = ('user', 'logro')
        verbose_name = 'Logro de Usuario'

    def __str__(self):
        return f"{self.user.username} → {self.logro.nombre}"


# ── Huesos de Milo (moneda interna) ──────────────────────────────────────────

class HuesoTransaccion(TimeStampedModel):
    """Records each earning/spending of Milo Bones."""
    TIPOS = [
        ('ganado', '🦴 Ganado'),
        ('gastado', '🛒 Gastado'),
        ('bonus', '🎁 Bonus'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='huesos_transacciones')
    tipo = models.CharField(max_length=10, choices=TIPOS, default='ganado')
    cantidad = models.IntegerField()
    descripcion = models.CharField(max_length=200)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.tipo} {self.cantidad} huesos"


# ── Museo Virtual / Juego de Pintar ──────────────────────────────────────────

class Artwork(TimeStampedModel):
    """Obra de arte guardada por un estudiante en el juego de pintar."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='artworks')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='artworks')
    vocabulary_item = models.ForeignKey(
        'content.VocabularyItem', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='artworks'
    )
    canvas_data = models.TextField(help_text='Base64 del canvas pintado por el estudiante')
    title = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Obra de Arte'
        verbose_name_plural = 'Obras de Arte'
        ordering = ['-created_at']

    def __str__(self):
        return f"Obra de {self.user.username}: {self.title}"


class PaintingWord(TimeStampedModel):
    """Palabras que el profesor define para un juego de pintar."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='painting_words')
    word = models.CharField(max_length=100, help_text='Palabra que el estudiante debe dibujar')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.game.title}: {self.word}"


# ── Tienda y Habitación de Milo ───────────────────────────────────────────────

class TiendaItem(TimeStampedModel):
    """An item available in the Milo store."""
    CATEGORIA_CHOICES = [
        ('mueble', '🛋️ Mueble'),
        ('decoracion', '🖼️ Decoración'),
        ('electronico', '📺 Electrónico'),
        ('planta', '🌿 Planta/Natural'),
        ('especial', '✨ Especial'),
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='decoracion')
    costo_huesos = models.IntegerField(default=25)
    icono = models.CharField(max_length=10, default='🛋️')
    imagen = models.ImageField(upload_to='tienda/', blank=True, null=True,
                               help_text='Imagen del objeto en la habitación')
    # Which minigame this item unlocks (optional)
    juego_desbloqueado = models.ForeignKey(
        'Game', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='desbloqueado_por',
        help_text='Minijuego que se desbloquea al comprar este objeto'
    )
    posicion_x = models.IntegerField(default=0, help_text='Posición X en la habitación (%)')
    posicion_y = models.IntegerField(default=0, help_text='Posición Y en la habitación (%)')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Item de Tienda'
        verbose_name_plural = 'Items de Tienda'
        ordering = ['order', 'costo_huesos']

    def __str__(self):
        return f"{self.icono} {self.nombre} ({self.costo_huesos} 🦴)"


class InventarioEstudiante(TimeStampedModel):
    """Items owned by a student."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='inventario')
    item = models.ForeignKey(TiendaItem, on_delete=models.CASCADE, related_name='propietarios')
    colocado_en_habitacion = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'item')
        verbose_name = 'Inventario'

    def __str__(self):
        return f"{self.user.username} → {self.item.nombre}"

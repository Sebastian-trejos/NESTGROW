from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel, ActiveModel
from apps.content.models import Category


class Game(TimeStampedModel, ActiveModel):
    GAME_TYPES = [
        ('drag_and_drop', '🖱️ Arrastra y Suelta'),
        ('word_search', '🔍 Sopa de Letras'),
        ('puzzle', '🧩 Rompecabezas'),
        ('audio_matching', '🎵 Juego de Audio'),
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
    points_reward = models.IntegerField(default=10)
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
    time_spent = models.IntegerField(default=0, help_text='Segundos jugados')

    class Meta:
        verbose_name = 'Progreso'
        verbose_name_plural = 'Progresos'
        unique_together = ('user', 'game')

    def percentage(self):
        if self.max_score == 0:
            return 0
        return int((self.score / self.max_score) * 100)

    def __str__(self):
        return f"{self.user} - {self.game} ({self.score} pts)"


class Score(TimeStampedModel):
    """Individual score record per attempt."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField()
    time_spent = models.IntegerField(default=0)

    class Meta:
        ordering = ['-score', 'time_spent']

    def __str__(self):
        return f"{self.user.username}: {self.score} en {self.game.title}"

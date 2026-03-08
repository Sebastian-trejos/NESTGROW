from django.contrib import admin
from .models import Game, UserProgress, Score


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'game_type', 'category', 'difficulty', 'points_reward', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('game_type', 'difficulty', 'category')
    search_fields = ('title',)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'score', 'completed', 'attempts')
    list_filter = ('completed',)


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'score', 'time_spent', 'created_at')
    list_filter = ('game',)

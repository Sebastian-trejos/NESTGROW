from django.contrib import admin
from .models import Game, UserProgress, Score, Logro, LogroUsuario, HuesoTransaccion, Artwork, PaintingWord, TiendaItem, InventarioEstudiante


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'game_type', 'category', 'difficulty', 'points_reward', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('game_type', 'difficulty', 'category')
    search_fields = ('title',)


class PaintingWordInline(admin.TabularInline):
    model = PaintingWord
    extra = 3
    fields = ('word', 'order')


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'score', 'completed', 'attempts')
    list_filter = ('completed',)


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'score', 'max_score', 'time_spent', 'created_at')
    list_filter = ('game',)


@admin.register(Logro)
class LogroAdmin(admin.ModelAdmin):
    list_display = ('icono', 'nombre', 'categoria', 'condicion_valor', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('categoria', 'is_active')


@admin.register(LogroUsuario)
class LogroUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'logro', 'visto', 'created_at')
    list_filter = ('visto',)


@admin.register(HuesoTransaccion)
class HuesoTransaccionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'cantidad', 'descripcion', 'created_at')
    list_filter = ('tipo',)


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'title', 'created_at')
    list_filter = ('game',)
    search_fields = ('user__username', 'title')


@admin.register(PaintingWord)
class PaintingWordAdmin(admin.ModelAdmin):
    list_display = ('game', 'word', 'order')
    list_filter = ('game',)


@admin.register(TiendaItem)
class TiendaItemAdmin(admin.ModelAdmin):
    list_display = ('icono', 'nombre', 'categoria', 'costo_huesos', 'juego_entretenimiento', 'posicion_x', 'posicion_y', 'is_active', 'order')
    list_editable = ('costo_huesos', 'juego_entretenimiento', 'posicion_x', 'posicion_y', 'is_active', 'order')
    list_filter = ('categoria', 'juego_entretenimiento', 'is_active')
    search_fields = ('nombre',)


@admin.register(InventarioEstudiante)
class InventarioEstudianteAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'colocado_en_habitacion', 'created_at')
    list_filter = ('colocado_en_habitacion',)
    search_fields = ('user__username', 'item__nombre')

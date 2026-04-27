from django.contrib import admin
from .models import (
    Taller, BloqueTaller, BloqueMinijuego, BloquePregunta,
    OpcionRespuesta, RespuestaEstudiante, SesionTaller,
)


class BloqueTallerInline(admin.TabularInline):
    model = BloqueTaller
    extra = 0
    ordering = ['orden']
    fields = ('orden', 'tipo')
    readonly_fields = ('orden', 'tipo')


@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'profesor', 'salon', 'is_active', 'puntos_xp', 'huesos_recompensa', 'created_at')
    list_filter = ('is_active', 'salon')
    search_fields = ('titulo', 'profesor__username', 'profesor__first_name')
    inlines = [BloqueTallerInline]


@admin.register(BloqueTaller)
class BloqueTallerAdmin(admin.ModelAdmin):
    list_display = ('taller', 'orden', 'tipo', 'created_at')
    list_filter = ('tipo',)
    ordering = ('taller', 'orden')


class OpcionRespuestaInline(admin.TabularInline):
    model = OpcionRespuesta
    extra = 0


@admin.register(BloquePregunta)
class BloquePreguntaAdmin(admin.ModelAdmin):
    list_display = ('enunciado', 'tipo_respuesta', 'puntaje_parcial')
    list_filter = ('tipo_respuesta',)
    inlines = [OpcionRespuestaInline]


@admin.register(SesionTaller)
class SesionTallerAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'taller', 'completada', 'puntos_obtenidos', 'huesos_ganados', 'bloque_actual')
    list_filter = ('completada',)
    search_fields = ('estudiante__username', 'taller__titulo')


@admin.register(RespuestaEstudiante)
class RespuestaEstudianteAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'pregunta', 'es_correcta', 'created_at')
    list_filter = ('es_correcta',)

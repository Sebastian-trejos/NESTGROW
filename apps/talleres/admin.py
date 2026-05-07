from django.contrib import admin
from .models import (
    Taller, BloqueTaller, BloqueMinijuego, BloquePregunta,
    OpcionRespuesta, RespuestaEstudiante, SesionTaller,
    Periodo, AsignacionTaller, AsignacionMinijuego, RegistroMinijuegoPeriodo,
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


# ── Periodos ──────────────────────────────────────────────────────────────────

class AsignacionTallerInline(admin.TabularInline):
    model = AsignacionTaller
    extra = 1
    fields = ('taller', 'orden')
    ordering = ['orden']


class AsignacionMinijuegoInline(admin.TabularInline):
    model = AsignacionMinijuego
    extra = 1
    fields = ('game', 'orden')
    ordering = ['orden']


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'salon', 'fecha_inicio', 'fecha_fin', 'is_activo', 'cerrado', 'estado')
    list_filter = ('is_activo', 'cerrado', 'salon')
    search_fields = ('titulo', 'salon__nombre')
    inlines = [AsignacionTallerInline, AsignacionMinijuegoInline]
    readonly_fields = ('estado',)

    def estado(self, obj):
        estados = {
            'activo': '🟢 Activo',
            'cerrado': '⚫ Cerrado',
            'vencido': '🔴 Vencido',
            'futuro': '🔵 Futuro',
        }
        return estados.get(obj.estado, obj.estado)
    estado.short_description = 'Estado'


@admin.register(RegistroMinijuegoPeriodo)
class RegistroMinijuegoPeriodoAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'asignacion', 'periodo', 'score', 'max_score', 'completado', 'revisado', 'created_at')
    list_filter = ('completado', 'revisado', 'periodo')
    search_fields = ('estudiante__username', 'asignacion__game__title')

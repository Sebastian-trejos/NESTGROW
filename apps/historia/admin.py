from django.contrib import admin
from .models import (
    SeccionHistoria, SeccionDesbloqueada, Leccion,
    ActividadLeccion, ProgresoLeccion, RespuestaActividad,
)


class LeccionInline(admin.TabularInline):
    model = Leccion
    fields = ('orden', 'titulo', 'icono_emoji', 'puntos_xp', 'huesos_recompensa', 'tiempo_estimado_minutos')
    extra = 0
    ordering = ('orden',)


class ActividadInline(admin.TabularInline):
    model = ActividadLeccion
    fields = ('orden', 'tipo', 'puntos_actividad')
    extra = 0
    ordering = ('orden',)


@admin.register(SeccionHistoria)
class SeccionHistoriaAdmin(admin.ModelAdmin):
    list_display = ('orden', 'icono_emoji', 'titulo', 'color_hex', 'is_desbloqueada_por_defecto')
    list_display_links = ('titulo',)
    ordering = ('orden',)
    inlines = [LeccionInline]


@admin.register(SeccionDesbloqueada)
class SeccionDesbloqueadaAdmin(admin.ModelAdmin):
    list_display = ('seccion', 'salon', 'desbloqueada_por', 'desbloqueada_en')
    list_filter = ('seccion',)


@admin.register(Leccion)
class LeccionAdmin(admin.ModelAdmin):
    list_display = ('seccion', 'orden', 'icono_emoji', 'titulo', 'puntos_xp', 'huesos_recompensa')
    list_filter = ('seccion',)
    ordering = ('seccion__orden', 'orden')
    inlines = [ActividadInline]


@admin.register(ActividadLeccion)
class ActividadLeccionAdmin(admin.ModelAdmin):
    list_display = ('leccion', 'orden', 'tipo', 'puntos_actividad')
    list_filter = ('tipo', 'leccion__seccion')
    ordering = ('leccion__seccion__orden', 'leccion__orden', 'orden')


@admin.register(ProgresoLeccion)
class ProgresoLeccionAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'leccion', 'completada', 'estrellas', 'intentos', 'completada_en')
    list_filter = ('completada', 'estrellas')
    readonly_fields = ('completada_en',)


@admin.register(RespuestaActividad)
class RespuestaActividadAdmin(admin.ModelAdmin):
    list_display = ('progreso', 'actividad', 'es_correcta', 'respondida_en')
    list_filter = ('es_correcta',)

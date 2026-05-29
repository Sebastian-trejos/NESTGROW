from django.contrib import admin
from .models import MensajeChat, PromptTemplate, LlamadaIA


@admin.register(MensajeChat)
class MensajeChatAdmin(admin.ModelAdmin):
    list_display = ('profesor', 'rol', 'modo', 'motor_usado', 'created_at')
    list_filter = ('rol', 'modo', 'motor_usado')
    search_fields = ('profesor__username', 'contenido')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'version', 'activo', 'updated_at')
    list_filter = ('activo',)
    search_fields = ('nombre', 'system')
    readonly_fields = ('updated_at',)
    ordering = ('nombre',)
    fieldsets = (
        (None, {
            'fields': ('nombre', 'activo', 'version'),
        }),
        ('Prompt', {
            'fields': ('system',),
            'classes': ('wide',),
        }),
        ('Notas internas', {
            'fields': ('notas', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(LlamadaIA)
class LlamadaIAAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'motor', 'proposito', 'latencia_ms', 'exito', 'cache_hit', 'usuario')
    list_filter = ('motor', 'exito', 'cache_hit', 'proposito')
    search_fields = ('proposito', 'usuario__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

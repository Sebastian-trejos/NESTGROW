from django.contrib import admin
from .models import MensajeChat


@admin.register(MensajeChat)
class MensajeChatAdmin(admin.ModelAdmin):
    list_display = ('profesor', 'rol', 'modo', 'motor_usado', 'created_at')
    list_filter = ('rol', 'modo', 'motor_usado')
    search_fields = ('profesor__username', 'contenido')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, VocabularyItem, VocabularioDesbloqueado, HitoVocabulario


class VocabularyItemInline(admin.TabularInline):
    model = VocabularyItem
    extra = 2
    fields = ('word_en', 'word_es', 'descripcion_es', 'pronunciacion_es',
              'imagen_thumb', 'difficulty', 'is_unlocked_by_default', 'orden', 'is_active')
    readonly_fields = ('imagen_thumb',)

    def imagen_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px">', obj.image.url)
        return '—'
    imagen_thumb.short_description = 'Imagen'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'name_en', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'name_en')
    inlines = [VocabularyItemInline]


@admin.register(VocabularyItem)
class VocabularyItemAdmin(admin.ModelAdmin):
    list_display = ('word_en', 'word_es', 'category', 'difficulty',
                    'is_unlocked_by_default', 'orden', 'is_active')
    list_filter = ('category', 'difficulty', 'is_unlocked_by_default', 'is_active')
    list_editable = ('orden', 'is_unlocked_by_default', 'is_active')
    search_fields = ('word_en', 'word_es', 'descripcion_es')
    ordering = ('category__order', 'orden')

    def save_model(self, request, obj, form, change):
        """
        Q3 — Traducción automática con MyMemory:
        Si el profesor guardó word_es pero word_en está vacío (o viceversa),
        auto-completa con MyMemory.
        """
        try:
            from apps.asistente.services import traducir_mymemory
            if obj.word_es and not obj.word_en:
                traduccion = traducir_mymemory(obj.word_es, origen='es', destino='en')
                if traduccion:
                    obj.word_en = traduccion
            elif obj.word_en and not obj.word_es:
                traduccion = traducir_mymemory(obj.word_en, origen='en', destino='es')
                if traduccion:
                    obj.word_es = traduccion
        except Exception:
            pass  # Traducción es best-effort; no bloquea el guardado
        super().save_model(request, obj, form, change)


@admin.register(VocabularioDesbloqueado)
class VocabularioDesbloqueadoAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'item', 'fuente', 'desbloqueado_en')
    list_filter = ('fuente', 'item__category')
    search_fields = ('estudiante__username', 'item__word_en')
    raw_id_fields = ('estudiante', 'item')
    date_hierarchy = 'desbloqueado_en'


@admin.register(HitoVocabulario)
class HitoVocabularioAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'palabras_cantidad', 'huesos_ganados', 'entregado_en')
    list_filter = ('palabras_cantidad',)
    search_fields = ('estudiante__username',)

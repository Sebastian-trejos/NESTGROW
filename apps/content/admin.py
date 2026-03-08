from django.contrib import admin
from .models import Category, VocabularyItem


class VocabularyItemInline(admin.TabularInline):
    model = VocabularyItem
    extra = 3
    fields = ('word_en', 'word_es', 'image', 'audio', 'difficulty', 'is_active')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'name_en', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'name_en')
    inlines = [VocabularyItemInline]


@admin.register(VocabularyItem)
class VocabularyItemAdmin(admin.ModelAdmin):
    list_display = ('word_en', 'word_es', 'category', 'difficulty', 'is_active')
    list_filter = ('category', 'difficulty', 'is_active')
    search_fields = ('word_en', 'word_es')

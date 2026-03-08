from django import forms
from .models import Game
from apps.content.models import Category, VocabularyItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'name_en', 'icon', 'description', 'color', 'order')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Animales'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Animals'}),
            'icon': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nombre en Español',
            'name_en': 'Name in English',
            'icon': 'Ícono',
            'description': 'Descripción',
            'color': 'Color de la tarjeta',
            'order': 'Orden de aparición',
        }


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('title', 'title_en', 'description', 'game_type', 'category',
                  'difficulty', 'points_reward', 'time_limit', 'order', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Animales - Arrastra y Suelta'}),
            'title_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Animals Drag & Drop'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                                  'placeholder': 'Descripción corta del juego...'}),
            'game_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'points_reward': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': 0,
                                                    'placeholder': '0 = sin límite de tiempo'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Título del juego (Español)',
            'title_en': 'Title (English)',
            'description': 'Descripción',
            'game_type': 'Tipo de juego',
            'category': 'Categoría de vocabulario',
            'difficulty': 'Dificultad',
            'points_reward': 'Puntos que otorga',
            'time_limit': 'Límite de tiempo (segundos)',
            'order': 'Orden',
            'is_active': '¿Activo? (visible para estudiantes)',
        }


class VocabularyItemForm(forms.ModelForm):
    class Meta:
        model = VocabularyItem
        fields = ('word_es', 'word_en', 'hint', 'difficulty', 'image', 'audio', 'is_active')
        widgets = {
            'word_es': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Perro'}),
            'word_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Dog'}),
            'hint': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Man\'s best friend'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'audio': forms.FileInput(attrs={'class': 'form-control', 'accept': 'audio/*'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'word_es': 'Palabra en Español',
            'word_en': 'Word in English',
            'hint': 'Pista o contexto',
            'difficulty': 'Dificultad',
            'image': 'Imagen (opcional)',
            'audio': 'Audio de pronunciación (opcional)',
            'is_active': '¿Activa?',
        }

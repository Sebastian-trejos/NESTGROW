from django import forms
from .models import Taller


class TallerForm(forms.ModelForm):
    class Meta:
        model = Taller
        fields = ('titulo', 'descripcion', 'salon', 'puntos_xp', 'huesos_recompensa', 'is_active')
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Taller de Animales en Inglés'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Descripción corta del taller...'
            }),
            'salon': forms.Select(attrs={'class': 'form-select'}),
            'puntos_xp': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'huesos_recompensa': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'titulo': 'Título del taller',
            'descripcion': 'Descripción (opcional)',
            'salon': 'Asignar a salón (opcional)',
            'puntos_xp': 'XP que otorga al completarse',
            'huesos_recompensa': 'Huesos de Milo al completar 🦴',
            'is_active': '¿Publicado? (visible para estudiantes)',
        }

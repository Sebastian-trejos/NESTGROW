from django import forms
from .models import Taller, Periodo
from apps.content.models import Category
from apps.games.models import Game


class TallerForm(forms.ModelForm):
    categorias_vocabulario = forms.ModelMultipleChoiceField(
        queryset=Category.active.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'vocab-cat-checkbox'}),
        label='Categorías de vocabulario que desbloquea',
        help_text='Las palabras de estas categorías se desbloquearán al completar el taller.',
    )

    class Meta:
        model = Taller
        fields = ('titulo', 'descripcion', 'puntos_xp', 'huesos_recompensa',
                  'categorias_vocabulario', 'is_active')
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Taller de Animales en Inglés'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Descripción corta del taller...'
            }),
            'puntos_xp': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'huesos_recompensa': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'titulo': 'Título del taller',
            'descripcion': 'Descripción (opcional)',
            'puntos_xp': 'XP que otorga al completarse',
            'huesos_recompensa': 'Huesos de Milo al completar 🦴',
            'is_active': '¿Publicado? (visible para estudiantes)',
        }


class PeriodoForm(forms.ModelForm):
    """Formulario para crear o editar un Período."""

    talleres_asignados = forms.ModelMultipleChoiceField(
        queryset=Taller.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'periodo-checkbox'}),
        label='Talleres del período (máx. 5)',
        help_text='Talleres publicados disponibles para este período.',
    )

    minijuegos_asignados = forms.ModelMultipleChoiceField(
        queryset=Game.objects.filter(is_active=True).order_by('title'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'periodo-checkbox'}),
        label='Minijuegos del período (máx. 5)',
    )

    class Meta:
        model = Periodo
        fields = ('titulo', 'color', 'salon', 'fecha_inicio', 'fecha_fin', 'meta_historia')
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Período 1 — Mayo 2026',
            }),
            'color': forms.RadioSelect(attrs={'class': 'color-radio'}),
            'salon': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'meta_historia': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0,
                'placeholder': '0 = sin meta',
            }),
        }
        labels = {
            'titulo': 'Título del período',
            'color': 'Color del encabezado',
            'salon': 'Salón',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha límite',
            'meta_historia': 'Meta de estrellas de historia ⭐ (0 = sin meta)',
        }

    def __init__(self, *args, salon_qs=None, profesor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if salon_qs is not None:
            self.fields['salon'].queryset = salon_qs
        # Talleres disponibles: todos los publicados del profesor (sin filtro por salón)
        talleres_qs = Taller.objects.filter(is_active=True)
        if profesor is not None:
            talleres_qs = talleres_qs.filter(profesor=profesor)
        self.fields['talleres_asignados'].queryset = talleres_qs.order_by('titulo')
        # Al editar, pre-seleccionar asignaciones existentes
        if self.instance and self.instance.pk:
            self.fields['talleres_asignados'].initial = list(
                self.instance.talleres_asignados.values_list('taller_id', flat=True)
            )
            self.fields['minijuegos_asignados'].initial = list(
                self.instance.minijuegos_asignados.values_list('game_id', flat=True)
            )

    def clean(self):
        cleaned = super().clean()
        talleres = cleaned.get('talleres_asignados', [])
        minijuegos = cleaned.get('minijuegos_asignados', [])
        if len(talleres) > 5:
            self.add_error('talleres_asignados', 'Máximo 5 talleres por período.')
        if len(minijuegos) > 5:
            self.add_error('minijuegos_asignados', 'Máximo 5 minijuegos por período.')
        fi = cleaned.get('fecha_inicio')
        ff = cleaned.get('fecha_fin')
        if fi and ff and ff < fi:
            self.add_error('fecha_fin', 'La fecha límite debe ser posterior a la de inicio.')
        return cleaned

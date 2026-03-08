from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, ProfesorProfile, EstudianteProfile


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label='Nombre')
    last_name = forms.CharField(max_length=50, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Correo electrónico')
    role = forms.ChoiceField(
        choices=[('profesor', '👩‍🏫 Soy Profesor'), ('estudiante', '🎒 Soy Estudiante')],
        label='¿Quién eres?',
        widget=forms.RadioSelect
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-control'})
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tu usuario'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '••••••••'
        })


class ProfesorProfileForm(forms.ModelForm):
    class Meta:
        model = ProfesorProfile
        fields = ('institucion', 'grado_a_cargo')
        widgets = {
            'institucion': forms.TextInput(attrs={'class': 'form-control'}),
            'grado_a_cargo': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EstudianteProfileForm(forms.ModelForm):
    class Meta:
        model = EstudianteProfile
        fields = ('grado',)
        widgets = {
            'grado': forms.Select(attrs={'class': 'form-select'}),
        }


class UnirseClaseForm(forms.Form):
    codigo_clase = forms.CharField(
        max_length=6,
        label='Código de clase',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center fs-4 letter-spacing-wide',
            'placeholder': 'ABC123',
            'maxlength': '6',
            'style': 'text-transform: uppercase;'
        })
    )

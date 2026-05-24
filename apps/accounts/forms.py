from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, ProfesorProfile, EstudianteProfile, Salon


def fc(placeholder='', extra=None):
    """Helper to build form-control widget attrs."""
    attrs = {'class': 'form-control'}
    if placeholder:
        attrs['placeholder'] = placeholder
    if extra:
        attrs.update(extra)
    return attrs


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label='Nombre',
                                  widget=forms.TextInput(attrs=fc('Tu nombre')))
    last_name = forms.CharField(max_length=50, required=True, label='Apellido',
                                 widget=forms.TextInput(attrs=fc('Tu apellido')))
    email = forms.EmailField(required=True, label='Correo electrónico',
                              widget=forms.EmailInput(attrs=fc('tucorreo@gmail.com')))
    role = forms.ChoiceField(
        choices=[('profesor', '👩‍🏫 Soy Profesor'), ('estudiante', '🎒 Soy Estudiante')],
        label='¿Quién eres?', widget=forms.RadioSelect
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-control'})
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password1'].help_text = (
            'Mínimo 8 caracteres, al menos un número. '
            'Evita contraseñas comunes como "12345678" o "password1".'
        )


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Tu usuario', 'autocomplete': 'username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••', 'autocomplete': 'current-password'})


# ── Profesor ──────────────────────────────────────────────────────────────────

class ProfesorUserForm(forms.ModelForm):
    """Edit basic user data for professor."""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs=fc('Nombre')),
            'last_name': forms.TextInput(attrs=fc('Apellido')),
            'email': forms.EmailInput(attrs=fc('tucorreo@gmail.com')),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }


class ProfesorProfileForm(forms.ModelForm):
    class Meta:
        model = ProfesorProfile
        fields = ('institucion',)
        widgets = {
            'institucion': forms.TextInput(attrs=fc('Nombre de la institución')),
        }
        labels = {'institucion': 'Institución educativa'}


class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ('nombre', 'grado', 'descripcion', 'is_active')
        widgets = {
            'nombre': forms.TextInput(attrs=fc('Ej: 3°A, 4°B')),
            'grado': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs=fc('Descripción opcional')),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre del salón',
            'grado': 'Grado',
            'descripcion': 'Descripción',
            'is_active': '¿Activo?',
        }


# ── Estudiante ────────────────────────────────────────────────────────────────

class EstudianteUserForm(forms.ModelForm):
    """Edit basic user data for student."""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name')
        widgets = {
            'first_name': forms.TextInput(attrs=fc('Nombre')),
            'last_name': forms.TextInput(attrs=fc('Apellido')),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }


class EstudianteProfileForm(forms.ModelForm):
    class Meta:
        model = EstudianteProfile
        fields = ('grado', 'correo_padre')
        widgets = {
            'grado': forms.Select(attrs={'class': 'form-select'}),
            'correo_padre': forms.EmailInput(attrs=fc('correo@ejemplo.com')),
        }
        labels = {
            'grado': 'Grado',
            'correo_padre': 'Correo del padre/madre de familia',
        }


class UnirseClaseForm(forms.Form):
    codigo_clase = forms.CharField(
        max_length=6, label='Código de clase',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center fs-4',
            'placeholder': 'ABC123', 'maxlength': '6',
            'style': 'text-transform:uppercase;letter-spacing:6px'
        })
    )

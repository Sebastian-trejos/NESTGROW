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
    role = forms.ChoiceField(
        choices=[('profesor', '👩‍🏫 Soy Profesor'), ('estudiante', '🎒 Soy Estudiante')],
        label='¿Quién eres?', widget=forms.RadioSelect
    )
    grado = forms.ChoiceField(
        choices=[('', '— Selecciona tu grado —')] + list(EstudianteProfile.GRADO_CHOICES),
        required=False,
        label='Grado',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'role', 'grado', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.RadioSelect, forms.Select)):
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

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        grado = cleaned_data.get('grado')
        if role == 'estudiante' and not grado:
            self.add_error('grado', 'Los estudiantes deben seleccionar su grado.')
        return cleaned_data


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
        fields = ('institucion', 'foto_perfil')
        widgets = {
            'institucion': forms.TextInput(attrs=fc('Nombre de la institución')),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'institucion': 'Institución educativa',
            'foto_perfil': 'Foto de perfil',
        }


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
    """Grado y correo_padre ahora son gestionados exclusivamente por el profesor."""
    class Meta:
        model = EstudianteProfile
        fields = ()  # Profesor gestiona grado y correo_padre


class GestionarEstudianteForm(forms.ModelForm):
    """Formulario que usa el profesor para editar datos de un estudiante."""
    class Meta:
        model = EstudianteProfile
        fields = ('grado', 'correo_padre', 'numero_lista')
        widgets = {
            'grado': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'correo_padre': forms.EmailInput(attrs=fc('correo@ejemplo.com', {'class': 'form-control form-control-sm'})),
            'numero_lista': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm text-center',
                'min': '1', 'max': '99', 'style': 'width:60px'
            }),
        }
        labels = {
            'grado': 'Grado',
            'correo_padre': 'Correo acudiente',
            'numero_lista': 'N° Lista',
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

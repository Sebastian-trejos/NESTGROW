from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import TimeStampedModel


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='estudiante')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def is_profesor(self):
        return self.role == 'profesor'

    def is_estudiante(self):
        return self.role == 'estudiante'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class ProfesorProfile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profesor_profile')
    institucion = models.CharField(max_length=200, blank=True)
    grado_a_cargo = models.CharField(max_length=100, blank=True,
                                     help_text="Ej: 3°, 4°, 5° primaria")
    codigo_clase = models.CharField(max_length=10, unique=True, blank=True,
                                    help_text="Código para que los estudiantes se unan")

    def save(self, *args, **kwargs):
        if not self.codigo_clase:
            import random, string
            self.codigo_clase = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profesor: {self.user.get_full_name() or self.user.username}"


class EstudianteProfile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='estudiante_profile')
    profesor = models.ForeignKey(
        ProfesorProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='estudiantes'
    )
    grado = models.CharField(max_length=20, blank=True,
                             choices=[
                                 ('1', '1° Primaria'), ('2', '2° Primaria'),
                                 ('3', '3° Primaria'), ('4', '4° Primaria'),
                                 ('5', '5° Primaria'),
                             ])
    puntos_totales = models.IntegerField(default=0)
    nivel = models.IntegerField(default=1)

    def actualizar_nivel(self):
        """Auto-update level based on points."""
        if self.puntos_totales >= 500:
            self.nivel = 5
        elif self.puntos_totales >= 300:
            self.nivel = 4
        elif self.puntos_totales >= 150:
            self.nivel = 3
        elif self.puntos_totales >= 50:
            self.nivel = 2
        else:
            self.nivel = 1
        self.save()

    def __str__(self):
        return f"Estudiante: {self.user.get_full_name() or self.user.username}"

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
    # Huesos de Milo wallet
    huesos = models.IntegerField(default=0, verbose_name='Huesos de Milo 🦴')

    def is_profesor(self):
        return self.role == 'profesor'

    def is_estudiante(self):
        return self.role == 'estudiante'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class Salon(TimeStampedModel):
    GRADO_CHOICES = [
        ('1', '1° Primaria'), ('2', '2° Primaria'),
        ('3', '3° Primaria'), ('4', '4° Primaria'),
        ('5', '5° Primaria'),
    ]
    profesor = models.ForeignKey('ProfesorProfile', on_delete=models.CASCADE, related_name='salones')
    nombre = models.CharField(max_length=100)
    grado = models.CharField(max_length=20, choices=GRADO_CHOICES)
    codigo_clase = models.CharField(max_length=8, unique=True, blank=True)
    descripcion = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.codigo_clase:
            import random, string
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                if not Salon.objects.filter(codigo_clase=code).exists():
                    self.codigo_clase = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.get_grado_display()})"

    class Meta:
        verbose_name = 'Salón'
        verbose_name_plural = 'Salones'
        ordering = ['grado', 'nombre']


class ProfesorProfile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profesor_profile')
    institucion = models.CharField(max_length=200, blank=True)
    codigo_clase = models.CharField(max_length=10, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.codigo_clase:
            import random, string
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                if not ProfesorProfile.objects.filter(codigo_clase=code).exists():
                    self.codigo_clase = code
                    break
        super().save(*args, **kwargs)

    def get_total_estudiantes(self):
        return EstudianteProfile.objects.filter(salon__profesor=self).count()

    def __str__(self):
        return f"Profesor: {self.user.get_full_name() or self.user.username}"


class EstudianteProfile(TimeStampedModel):
    GRADO_CHOICES = [
        ('1', '1° Primaria'), ('2', '2° Primaria'),
        ('3', '3° Primaria'), ('4', '4° Primaria'),
        ('5', '5° Primaria'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='estudiante_profile')
    salon = models.ForeignKey(Salon, on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')
    profesor = models.ForeignKey(ProfesorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')
    grado = models.CharField(max_length=20, blank=True, choices=GRADO_CHOICES)
    numero_identidad = models.CharField(max_length=20, blank=True, verbose_name='N° Tarjeta de Identidad')
    correo_padre = models.EmailField(blank=True, verbose_name='Correo del padre/madre de familia')
    puntos_totales = models.IntegerField(default=0)
    nivel = models.IntegerField(default=1)

    # Points required to level up from each level
    PUNTOS_POR_NIVEL = {
        1: 20,   # Level 1 → 2: 20 pts
        2: 30,   # Level 2 → 3: 30 pts
        3: 50,   # Level 3 → 4: 50 pts
        4: 80,   # Level 4 → 5: 80 pts
        5: 120,  # Level 5 → 6: 120 pts
        6: 160,  # Level 6 → 7: 160 pts
        7: 200,  # Level 7 → 8: 200 pts
        8: 250,  # Level 8+: 250 pts
    }
    MAX_NIVEL = 10

    def puntos_requeridos(self):
        """Points needed to reach next level from current level."""
        return self.PUNTOS_POR_NIVEL.get(self.nivel, 250)

    def actualizar_nivel(self):
        """Check if student leveled up, reset points if so, award bones."""
        requeridos = self.puntos_requeridos()
        subio = False
        while self.puntos_totales >= requeridos and self.nivel < self.MAX_NIVEL:
            self.puntos_totales -= requeridos
            self.nivel += 1
            subio = True
            requeridos = self.puntos_requeridos()
        # Always save current state (points + level)
        EstudianteProfile.objects.filter(pk=self.pk).update(
            puntos_totales=self.puntos_totales,
            nivel=self.nivel
        )
        if subio:
            # Award 15 Milo Bones on level up
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = self.user
            user.huesos += 15
            user.save(update_fields=['huesos'])
            try:
                from apps.games.models import HuesoTransaccion
                HuesoTransaccion.objects.create(
                    user=user, tipo='bonus', cantidad=15,
                    descripcion=f'🎉 ¡Subiste al Nivel {self.nivel}!'
                )
            except Exception:
                pass
        return subio

    def get_profesor(self):
        if self.salon:
            return self.salon.profesor
        return self.profesor

    def __str__(self):
        return f"Estudiante: {self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'

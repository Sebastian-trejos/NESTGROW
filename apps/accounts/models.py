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
    foto_perfil = models.ImageField(upload_to='profesores/fotos/', blank=True, null=True, verbose_name='Foto de perfil')

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
    numero_lista = models.CharField(max_length=10, blank=True, verbose_name='N° de Lista')
    correo_padre = models.EmailField(blank=True, verbose_name='Correo del padre/madre de familia')
    puntos_totales = models.IntegerField(default=0)
    nivel = models.IntegerField(default=1)
    total_estrellas_historia = models.IntegerField(default=0, verbose_name='Estrellas Modo Historia')

    # Avatar Emoji Kitchen
    avatar_emoji1 = models.CharField(max_length=10, blank=True, default='🐶')
    avatar_emoji2 = models.CharField(max_length=10, blank=True, default='🐱')
    avatar_color = models.CharField(max_length=10, blank=True, default='#6C63FF')
    avatar_kitchen_url = models.URLField(max_length=500, blank=True)

    # Puntos necesarios para subir de cada nivel al siguiente.
    # Calibrado para juegos con máximo 25/40/60 pts según dificultad.
    # Ritmo estimado: ~180 pts/semana (3 sesiones × 3 juegos × ~20 pts prom.)
    PUNTOS_POR_NIVEL = {
        # Principiante (1–10) — ~7 semanas de juego regular para completar
        1:  30,  2:  45,  3:  60,  4:  80,  5: 105,
        6: 130,  7: 160,  8: 195,  9: 235, 10: 280,
        # Intermedio (11–20) — ~35 semanas adicionales
        11: 330, 12: 385, 13: 445, 14: 510, 15: 580,
        16: 655, 17: 735, 18: 820, 19: 910, 20: 1005,
        # Avanzado (21–30)
        21: 1105, 22: 1210, 23: 1320, 24: 1435, 25: 1555,
        26: 1680, 27: 1810, 28: 1945, 29: 2085, 30: 2230,
        # Experto (31–40)
        31: 2380, 32: 2535, 33: 2695, 34: 2860, 35: 3030,
        36: 3205, 37: 3385, 38: 3570, 39: 3760, 40: 3955,
        # Maestro (41–49)
        41: 4155, 42: 4360, 43: 4570, 44: 4785, 45: 5005,
        46: 5230, 47: 5460, 48: 5695, 49: 5935,
    }
    MAX_NIVEL = 50

    def puntos_requeridos(self):
        """Points needed to reach next level from current level."""
        return self.PUNTOS_POR_NIVEL.get(self.nivel, 24000)

    @property
    def puntos_acumulados(self):
        """Lifetime total points, never reset by level-ups."""
        total = self.puntos_totales
        for lvl in range(1, self.nivel):
            total += self.PUNTOS_POR_NIVEL.get(lvl, 0)
        return total

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
            # Award 5 Milo Bones on level up
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = self.user
            user.huesos += 5
            user.save(update_fields=['huesos'])
            try:
                from apps.games.models import HuesoTransaccion
                HuesoTransaccion.objects.create(
                    user=user, tipo='bonus', cantidad=5,
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

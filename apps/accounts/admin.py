from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ProfesorProfile, EstudianteProfile


class ProfesorProfileInline(admin.StackedInline):
    model = ProfesorProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Profesor'


class EstudianteProfileInline(admin.StackedInline):
    model = EstudianteProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Estudiante'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('NestGrow', {'fields': ('role', 'avatar', 'bio')}),
    )

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == 'profesor':
                return [ProfesorProfileInline]
            elif obj.role == 'estudiante':
                return [EstudianteProfileInline]
        return []


@admin.register(ProfesorProfile)
class ProfesorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institucion', 'codigo_clase', 'grado_a_cargo')
    search_fields = ('user__username', 'user__first_name', 'codigo_clase')


@admin.register(EstudianteProfile)
class EstudianteProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'grado', 'puntos_totales', 'nivel', 'profesor')
    list_filter = ('grado', 'nivel')
    search_fields = ('user__username', 'user__first_name')

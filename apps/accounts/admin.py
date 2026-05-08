from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ProfesorProfile, EstudianteProfile, Salon


class ProfesorProfileInline(admin.StackedInline):
    model = ProfesorProfile
    can_delete = False


class EstudianteProfileInline(admin.StackedInline):
    model = EstudianteProfile
    can_delete = False


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


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'grado', 'profesor', 'codigo_clase', 'is_active')
    list_filter = ('grado', 'is_active')
    search_fields = ('nombre', 'codigo_clase', 'profesor__user__username')


@admin.register(ProfesorProfile)
class ProfesorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institucion')
    search_fields = ('user__username', 'user__first_name')


@admin.register(EstudianteProfile)
class EstudianteProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'grado', 'salon', 'puntos_totales', 'nivel', 'correo_padre')
    list_filter = ('grado', 'nivel')
    search_fields = ('user__username', 'user__first_name', 'numero_identidad')

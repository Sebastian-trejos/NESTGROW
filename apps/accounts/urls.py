from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Profesor
    path('dashboard/profesor/', views.dashboard_profesor, name='dashboard_profesor'),
    path('perfil/profesor/editar/', views.editar_perfil_profesor, name='editar_perfil_profesor'),
    path('salones/nuevo/', views.crear_salon, name='crear_salon'),
    path('salones/<int:pk>/editar/', views.editar_salon, name='editar_salon'),
    path('salones/<int:pk>/eliminar/', views.eliminar_salon, name='eliminar_salon'),
    path('salones/<int:pk>/', views.detalle_salon, name='detalle_salon'),
    path('estudiante/<int:estudiante_pk>/informe/', views.enviar_informe, name='enviar_informe'),
    path('estudiante/<int:pk>/numero-lista/', views.set_numero_lista, name='set_numero_lista'),
    path('estudiante/<int:pk>/actualizar/', views.actualizar_estudiante, name='actualizar_estudiante'),
    path('salones/<int:pk>/subir-grado/', views.subir_grado_salon, name='subir_grado_salon'),

    # Estudiante
    path('dashboard/estudiante/', views.dashboard_estudiante, name='dashboard_estudiante'),
    path('perfil/estudiante/editar/', views.editar_perfil_estudiante, name='editar_perfil_estudiante'),
    path('avatar/guardar/', views.guardar_avatar, name='guardar_avatar'),
    path('unirse/', views.unirse_clase, name='unirse_clase'),

    # Legacy
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
]

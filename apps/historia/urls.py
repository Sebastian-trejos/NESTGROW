from django.urls import path
from . import views

app_name = 'historia'

urlpatterns = [
    # Placeholder images (PIL-generated)
    path('img/<str:nombre>.png', views.placeholder_img, name='placeholder_img'),

    # ── Estudiante ────────────────────────────────────────────────────────────
    path('', views.mapa_historia, name='mapa_historia'),
    path('leccion/<int:pk>/', views.ver_leccion, name='ver_leccion'),

    # AJAX endpoints
    path('api/responder/', views.guardar_respuesta, name='guardar_respuesta'),
    path('api/completar/<int:pk>/', views.completar_leccion, name='completar_leccion'),

    # ── Profesor ──────────────────────────────────────────────────────────────
    path('profesor/', views.panel_historia_profesor, name='panel_historia_profesor'),
    path('profesor/desbloquear/<int:pk>/', views.desbloquear_seccion, name='desbloquear_seccion'),
    path('profesor/bloquear/<int:pk>/', views.bloquear_seccion, name='bloquear_seccion'),
    path('profesor/progreso/<int:pk>/', views.progreso_seccion_profesor, name='progreso_seccion_profesor'),
]

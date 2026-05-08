from django.urls import path
from . import views

app_name = 'talleres'

urlpatterns = [
    # ── Profesor ──────────────────────────────────────────────────────────────
    path('', views.lista_talleres, name='lista'),
    path('nuevo/', views.crear_taller, name='crear'),
    path('<int:pk>/editar/', views.editar_taller, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_taller, name='eliminar'),
    path('<int:pk>/toggle/', views.toggle_taller, name='toggle'),
    path('<int:pk>/preview/', views.preview_taller, name='preview'),
    path('<int:pk>/resultados/', views.resultados_taller, name='resultados'),

    # AJAX — bloques
    path('<int:pk>/bloque/nuevo/', views.agregar_bloque, name='agregar_bloque'),
    path('bloque/<int:bpk>/eliminar/', views.eliminar_bloque, name='eliminar_bloque'),
    path('<int:pk>/bloques/ordenar/', views.mover_bloques, name='mover_bloques'),

    # ── Periodos — Profesor ───────────────────────────────────────────────────
    path('periodos/', views.lista_periodos, name='lista_periodos'),
    path('periodos/crear/', views.crear_periodo, name='crear_periodo'),
    path('periodos/<int:pk>/resultados/', views.resultados_periodo, name='resultados_periodo'),
    path('periodos/<int:pk>/cerrar/', views.cerrar_periodo, name='cerrar_periodo'),
    path('periodos/<int:pk>/eliminar/', views.eliminar_periodo, name='eliminar_periodo'),

    # ── Estudiante ────────────────────────────────────────────────────────────
    path('mis-talleres/', views.mis_talleres, name='mis_talleres'),
    path('<int:pk>/resolver/', views.resolver_taller, name='resolver'),
    path('<int:pk>/bloque/<int:bpk>/responder/', views.guardar_respuesta, name='responder'),
    path('<int:pk>/bloque/<int:bpk>/completar-minijuego/', views.score_bloque_minijuego, name='score_minijuego'),
    path('<int:pk>/resultado/', views.resultado_taller, name='resultado'),
    path('sesion/<int:pk>/resultado/', views.resultado_sesion, name='resultado_sesion'),
]

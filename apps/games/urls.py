from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    # Estudiantes
    path('', views.game_list, name='game_list'),
    path('<int:pk>/', views.game_detail, name='game_detail'),
    path('guardar-puntaje/', views.save_score, name='save_score'),

    # Profesor — Juegos
    path('gestionar/', views.gestionar_juegos, name='gestionar_juegos'),
    path('gestionar/nuevo/', views.crear_juego, name='crear_juego'),
    path('gestionar/<int:pk>/editar/', views.editar_juego, name='editar_juego'),
    path('gestionar/<int:pk>/eliminar/', views.eliminar_juego, name='eliminar_juego'),
    path('gestionar/<int:pk>/toggle/', views.toggle_juego, name='toggle_juego'),

    # Profesor — Categorías
    path('categorias/', views.gestionar_categorias, name='gestionar_categorias'),
    path('categorias/nueva/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),

    # Profesor — Vocabulario
    path('vocabulario/<int:categoria_pk>/', views.gestionar_vocabulario, name='gestionar_vocabulario'),
    path('vocabulario/<int:categoria_pk>/nueva/', views.crear_vocabulario, name='crear_vocabulario'),
    path('vocabulario/item/<int:pk>/editar/', views.editar_vocabulario, name='editar_vocabulario'),
    path('vocabulario/item/<int:pk>/eliminar/', views.eliminar_vocabulario, name='eliminar_vocabulario'),
]

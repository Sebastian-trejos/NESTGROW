from django.urls import path
from . import views

app_name = 'asistente'

urlpatterns = [
    path('', views.index, name='index'),
    path('analizar/', views.analizar, name='analizar'),
    path('limpiar/', views.limpiar_historial, name='limpiar_historial'),
]

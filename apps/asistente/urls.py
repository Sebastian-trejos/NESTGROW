from django.urls import path
from . import views

app_name = 'asistente'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('analizar/', views.analizar, name='analizar'),
    path('limpiar/', views.limpiar_historial, name='limpiar_historial'),
    path('milo-correccion/', views.milo_correccion, name='milo_correccion'),
]

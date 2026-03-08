from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/profesor/', views.dashboard_profesor, name='dashboard_profesor'),
    path('dashboard/estudiante/', views.dashboard_estudiante, name='dashboard_estudiante'),
    path('unirse/', views.unirse_clase, name='unirse_clase'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
]

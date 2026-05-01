from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('mi-vocabulario/', views.mi_vocabulario, name='mi_vocabulario'),
    path('<int:pk>/', views.category_detail, name='category_detail'),
]

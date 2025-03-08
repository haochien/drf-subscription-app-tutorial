from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check_basic, name='health_check_basic'),
    path('db/', views.health_check_db, name='health_check_db'),
]
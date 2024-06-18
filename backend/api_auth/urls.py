from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'test', views.TestModelViewSet)

urlpatterns = [
    #path('test/', views.TestModelViewSet.as_view({ 'get': 'list', 'post': 'create'})),
    #path('test/<int:pk>/', views.TestModelViewSet.as_view({ 'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('', include(router.urls)),
]

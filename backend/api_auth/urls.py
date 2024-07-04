from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'test', views.TestModelViewSet, basename='test_model')
router.register(r'test-protected', views.TestModelProtectedViewSet, basename='test_model_protect')

urlpatterns = [
    #path('test/', views.TestModelViewSet.as_view({ 'get': 'list', 'post': 'create'})),
    #path('test/<int:pk>/', views.TestModelViewSet.as_view({ 'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('', include(router.urls)),
    path('register/', views.CustomRegisterView.as_view(), name='auth_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google/login/', views.GoogleLoginView.as_view(), name='google_login'),
    path('google/callback/', views.GoogleOAuth2CallbackView.as_view(), name='google_callback'),
]

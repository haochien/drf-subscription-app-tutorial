import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import TestModel, Profile
from .serializers import TestModelSerializer, RegisterSerializer
import logging

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)
env = settings.ENV
User = get_user_model()

# Create your views here.
class TestModelViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer

    def list(self, request, *args, **kwargs):
        logger.info('TestModelViewSet list view called')
        logger.warning('Warning log in list view')
        return super().list(request, *args, **kwargs)


class TestModelProtectedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer
    

class CustomRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        auth_url = (
            'https://accounts.google.com/o/oauth2/v2/auth?'
            'redirect_uri={redirect_uri}&'
            'prompt=consent&'
            'response_type=code&'
            'client_id={client_id}&'
            'scope=openid%20email%20profile'
        ).format(
            redirect_uri=env('GOOGLE_OAUTH2_REDIRECT_URI'),
            client_id=env('GOOGL_CLIENT_ID'),
        )
        return redirect(auth_url)


class GoogleOAuth2CallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange authorization code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': env('GOOGL_CLIENT_ID'),
            'client_secret': env('GOOGL_SECRET'),
            'redirect_uri': env('GOOGLE_OAUTH2_REDIRECT_URI'),
            'grant_type': 'authorization_code'
        }
        response = requests.post(token_url, data=data)
        token_data = response.json()

        if 'error' in token_data:
            return Response(token_data, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_data.get('access_token')
        id_token = token_data.get('id_token')

        # Retrieve user info
        user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        user_info_response = requests.get(user_info_url, params={'access_token': access_token})
        if not response.ok:
            raise ValidationError('Failed to obtain user info from Google.')
        
        user_info = user_info_response.json()
        email = user_info.get('email')
        user_name = user_info.get('name')
        first_name = user_info.get('given_name')

        # Create or get user
        user, created = User.objects.get_or_create(email=email)
        user.last_login = timezone.now()
        if created:
            user.register_method = "google"
            user.save()
        
        # Update profile
        Profile.objects.update_or_create(
            user=user,
            defaults={'display_name': user_name, 'first_name': first_name}
        )

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
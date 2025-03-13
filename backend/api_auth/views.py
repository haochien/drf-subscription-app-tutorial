import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import TestModel, Profile, EmailVerification
from .serializers import TestModelSerializer, RegisterSerializer, ResendVerificationSerializer, CustomUserSerializer, ProfileSerializer
import logging
from .utils import send_verification_email, send_welcome_email

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
    
    def perform_create(self, serializer):
        user = serializer.save()
        # Create verification token
        verification = EmailVerification.objects.create(user=user)
        # Send verification email
        send_verification_email(user, verification.token)


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
            user.is_email_verified = True  # Google accounts have verified emails
            user.save()

            # Send welcome email to new Google users
            send_welcome_email(user)
        
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


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, token):
        try:
            verification = get_object_or_404(EmailVerification, token=token)
            
            if not verification.is_valid():
                return Response(
                    {'error': 'Verification link has expired or already been used'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            user = verification.user
            user.is_email_verified = True
            user.save()
            
            verification.is_used = True
            verification.save()
            
            # Send welcome email
            send_welcome_email(user)
            
            return Response({'message': 'Email verified successfully'})
            
        except Exception as e:
            logger.error(f"Email verification failed: {str(e)}")
            return Response(
                {'error': 'Invalid verification token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                if user.is_email_verified:
                    return Response(
                        {'message': 'Email already verified'}, 
                        status=status.HTTP_200_OK
                    )
                
                # Delete any existing verification tokens
                user.verification_tokens.all().delete()
                
                # Create new verification token
                verification = EmailVerification.objects.create(user=user)
                
                # Send verification email
                send_verification_email(user, verification.token)
                
                return Response(
                    {'message': 'Verification email sent successfully'}, 
                    status=status.HTTP_200_OK
                )
                
            except User.DoesNotExist:
                # Don't reveal that the user doesn't exist for security
                return Response(
                    {'message': 'If your account exists, a verification email will be sent'}, 
                    status=status.HTTP_200_OK
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        profile = user.profile
        
        # Serialize user data
        user_data = CustomUserSerializer(user).data
        
        # Serialize profile data
        profile_data = ProfileSerializer(profile).data
        
        # Combine data
        response_data = {
            **user_data,
            'profile': profile_data
        }
        
        return Response(response_data)
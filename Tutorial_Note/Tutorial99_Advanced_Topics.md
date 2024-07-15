# Advanced Topics

## 1. Blacklisting refresh token

### 1.1. Implement blacklist (with Redis caching setup) for refreshing refresh token and user logout

### 1.2. Strategy on clean up blacklist data

### 1.3. Logout all device

## 2. Password Reset

### 2.1. Email server setup

### 2.2. Reset password view setup




You are now a senior and professional software engineer. You need to guide me to finish my project.
The goal is to build a web app which allows users to subscribe membership and can view certain premium content.
I choose Django Rest Framework (DRF) as my backend, PostgreSQL as the database, and react JS (I started project with Vite) as my frontend.
In additional, I use Mantine as my react UI library to support my frontend development.
This web application will go production, and thus the set up in this project needs to be flexible enough to achieve develop and deploy in both development and production environment.
The backend and frontend will be deployed separately to different domains.
I require that the code should be written in clean, readable, structured and professional way.
Please based on standard app development requirement to structure the code and files in this project.

Currently I have finished certain login api in the backend part. I will provide you what I have done.
Please check my codes and continue on the project based on my question and instruction.
I will provide you my codes based markdown format.

My directory structure is as followings (I don't list all the folders and files here. I simply list the important files and folders so that you can have a brief idea on how the project is set up):

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ api_auth
│  │  ├─ models.py
│  │  ├─ serializers.py
│  │  ├─ signals.py
│  │  ├─ urls.py
│  │  ├─ views.py
│  ├─ backend
│  │  ├─ settings.py
│  │  ├─ urls.py
│  ├─ .env
│  ├─ manage.py
│  ├─ requirement.txt
├─ frontend/
│  ├─ public
│  ├─ src
│  │  ├─ assets
│  │  ├─ components
│  │  ├─ pages
│  │  │  ├─ Home.jsx
│  │  ├─ services
│  │  │  ├─ axiosConfig.js
│  │  ├─ App.jsx
│  │  ├─ main.jsx
│  ├─ .env
│  ├─ package.json
│  ├─ ...
```

In the backend DRF part, I have built up the authentication model and api.
I choose Simple JWT as main authentication method and Google OAuth as secondary authentication approach.
To allow user to login in with email, I customized my User model.
Besides, after the user register, I immediately create his/her profile data in Profile model.

Followings are the setup in my DRF:

Under ./backend/backend:

```python
# ./backend/backend/settings.py

from pathlib import Path
import environ
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = os.getenv('DRF_ENV_PATH', BASE_DIR / '.env')

ENV = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(ENV_PATH)

SECRET_KEY = ENV('SECRET_KEY')

DEBUG = ENV('DEBUG')

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'api_auth'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL = 'api_auth.User'

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': ENV('DATABASE_NAME'),
        'USER': ENV('DATABASE_USER'),
        'PASSWORD': ENV('DATABASE_PASSWORD'),
        'HOST': ENV('DATABASE_HOST', default='localhost'),
        'PORT': ENV('DATABASE_PORT', default=5432),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Rest Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# Simple JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
}



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'https://your-production-domain.com',
]
CORS_ALLOW_CREDENTIALS = True
```

```python
# ./backend/backend/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('api_auth.urls')),
]
```


Under ./backend/api_auth:

```python
# ./backend/api_auth/model.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):

  def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
    if not email:
        raise ValueError('Users must have an email address')
    now = timezone.now()
    email = self.normalize_email(email)
    user = self.model(
        email=email,
        is_staff=is_staff, 
        is_active=True,
        is_superuser=is_superuser, 
        last_login=now,
        date_joined=now, 
        **extra_fields
    )
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, password, **extra_fields):
    return self._create_user(email, password, False, False, **extra_fields)

  def create_superuser(self, email, password, **extra_fields):
    return self._create_user(email, password, True, True, **extra_fields)
  

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    REGISTRATION_CHOICES = [
        ('email', 'Email'),
        ('google', 'Google'),
    ]
    register_method = models.CharField(
        max_length=10,
        choices=REGISTRATION_CHOICES,
        default='email'
    )
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'auth_user' 


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    short_intro = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    link_twitter = models.CharField(max_length=200, blank=True, null=True)
    link_linkedin = models.CharField(max_length=200, blank=True, null=True)
    link_youtube = models.CharField(max_length=200, blank=True, null=True)
    link_facebook = models.CharField(max_length=200, blank=True, null=True)
    link_website = models.CharField(max_length=200, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}'s profile"

    class Meta:
        db_table = 'profile' 
```


```python
# ./backend/api_auth/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```


```python
# ./backend/api_auth/serializers.py

from rest_framework import serializers
from .models import TestModel, Profile
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_active', 'is_staff', 'last_login', 'date_joined', 'register_method')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('display_name', 'first_name', 'last_name', 'short_intro', 'bio', 
                  'link_twitter', 'link_linkedin', 'link_youtube', 'link_facebook', 'link_website')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('email', 'password', 'profile')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            register_method="email",
        )

        Profile.objects.update_or_create(user=user, defaults=profile_data)
        return user
```


```python
# ./backend/api_auth/views.py

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

env = settings.ENV
User = get_user_model()

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


```

```python
# ./backend/api_auth/urls.py

from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', views.CustomRegisterView.as_view(), name='auth_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google/login/', views.GoogleLoginView.as_view(), name='google_login'),
    path('google/callback/', views.GoogleOAuth2CallbackView.as_view(), name='google_callback'),
]

```

First question, do you understand my project setup? Is there anything you are not clear?
Do you have any comment or any suggestion can provide me for current backend setup?



-----

In api.js (I simply put api.js under src folder):

```js
// ./src/api.js

import axios from 'axios';
import { API_BASE_URL, ACCESS_TOKEN } from './constants';

const api = axios.create({
  baseURL: API_BASE_URL,
});s

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);


export default api;
```

Then I create a new ProtectedRoute.jsx under components fold:

```js
// ./src/components/ProtectedRoute.jsx

import { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";
import api from "../api";


function ProtectedRoute({ children }) {
    const [isAuthorized, setIsAuthorized] = useState(null);

    useEffect(() => {
        checkAuth().catch(() => setIsAuthorized(false))
    }, [])

    const getNewRefreshToken = async () => {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN);
        try {
            const res = await api.post("/auth/token/refresh/", {
                refresh: refreshToken,
            });
            if (res.status === 200) {
                localStorage.setItem(ACCESS_TOKEN, res.data.access)
                localStorage.setItem(REFRESH_TOKEN, res.data.refresh)
                setIsAuthorized(true)
            } else {
                setIsAuthorized(false)
            }
        } catch (error) {
            console.log(error);
            setIsAuthorized(false);
        }
    };

    const isAccessTokenExpired = async (token) => {
        const decodedToken = jwtDecode(token);
        const tokenExpirationTime = decodedToken.exp;
        const now = Date.now() / 1000;

        if (tokenExpirationTime < now) {
            await getNewRefreshToken();
        } else {
            setIsAuthorized(true);
        }        
    }

    const checkAuth = async () => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (!token) {
            setIsAuthorized(false);
            return;
        }
        
        await isAccessTokenExpired(token)

    };

    if (isAuthorized === null) {
        return <div>Check Authorization...</div>;
    }

    return isAuthorized ? children : <Navigate to="/login" />;
}

export default ProtectedRoute;
```


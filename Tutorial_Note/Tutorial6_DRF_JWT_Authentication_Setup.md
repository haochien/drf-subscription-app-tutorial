
# Simple JWT & Cunstomized User Model Setup

This project will use Django simplejwt as the main authentication method.

Besides, Google OAuth2 will also be integrated into this application as secondary authentication method.

In this chapter, we will first cover User model customization and Simple JWT setup.

## Set up Simple JWT in Django

### 1. install simple jwt library

```sh
pip install djangorestframework-simplejwt
```

### 2. Update settings.py

Add `rest_framework_simplejwt` in `INSTALLED_APPS`. And set up `REST_FRAMEWORK` and `SIMPLE_JWT` dictionaries in the `settings.py`

Please note that we temporarily set `ROTATE_REFRESH_TOKENS` and `BLACKLIST_AFTER_ROTATION` to False.

For better security setup, we should black list users' refresh token when user log out or refresh their refresh token.

This part will be covered in the advance lecture.

To make the tutorial not too complicated, we will simply refresh the refresh token and won't blacklist the refresh token in this chapter.

We keep the lifetime of access token and refresh token shorter to make sure the security

```python
# ./backend/settings.py

from datetime import timedelta

INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_simplejwt',
    'api_auth'
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
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
}

```

### 3. Create customized User Model

Since this project will use email address as authentication, the default `User` model (using username as authentication) does not match this requirement.
A customized `User` model is required.

The customized `User` subclasses Django `AbstractBaseUser`, giving it the methods, but none of the default fields.

The `UserManager` subclasses the `BaseUserManager` and overrides the methods `create_user` and `create_superuser`.

You can check more details about customized User model in the following two articles 

* [Django : Custom User Model & Allauth for OAuth](https://medium.com/@ksarthak4ever/django-custom-user-model-allauth-for-oauth-20c84888c318)
* [Custom users using Django REST framework](https://medium.com/@yashnarsamiyev2/custom-users-using-django-rest-framework-dda29f657e95)

#### a. create customized User model in model.py

```python
# ./api_auth/model.py

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

    # register_method can be used to differenciate Simple JWT login and Google OAuth2
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
    # REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'auth_user' 
```

#### b. (Optional) Create Profile Model

If you plan to build a relatively simple application where you don't anticipate needing much additional user information beyond basic details (e.g. first_name, last_name,...etc.), you can simply keep those simple information in the User model.

However, if you're building a more complex application or you anticipate needing to store various additional user details (like address, gender, preferences, etc.), creating a separate Profile model is a good idea.

Profile model will be included in this tutorial.

```python
# ./api_auth/model.py

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

Then we can set up django signal to make sure that the Profile data will be created right after the new user is created.

```python
# ./api_auth/signals.py

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

#### c. update settings.py

override `AUTH_USER_MODEL` in settings.py with the customized User model just created.

```python
# ./backend/settings.py

MIDDLEWARE = [
    ...
]

AUTH_USER_MODEL = 'api_auth.User'
```

### 4. Set up new Serializers for authentication

We need to set up a register serializers so that the users can register themselves via the register endpoint.

```python
# ./api_auth/serializers.py

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
        fields = ('email', 'password', 'first_name', 'last_name')

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

### 4. Create register and test view in views.py

Create a register view `CustomRegisterView` and and test view `TestModelProtectedViewSet` which required authentication.
In the original test view `TestModelViewSet`, add `permission_classes = [AllowAny]` so that we can access this page without authentication.

```python
# ./api_auth/views.py

from rest_framework import viewsets, generics, status
from .serializers import TestModelSerializer, RegisterSerializer

User = get_user_model()

# Create your views here.
class TestModelViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    ...


class TestModelProtectedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer
    

class CustomRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

```

### 5. Update urls.py

`register/` endpoint will be used for users to register.

`token/` endpoint will be used for users to login.

`token/refresh/` endpoint will be used to refresh  users' refresh token.

```python
# ./api_auth/urls.py

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'test', views.TestModelViewSet, basename='test_model')
router.register(r'test-protected', views.TestModelProtectedViewSet, basename='test_model_protect')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.CustomRegisterView.as_view(), name='auth_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

### 6. Testing

Usually, customized User model will be done before make first migration since it involves default User table change.

In our tutorial, we have made migration already and thus require clean-up in our `migrations` folder:

1. Delete all python scripts in the `./api_auth/migrations` folder except the `__init__.py`

2. Delete all tables in the database

3. create new migration scripts with `python manage.py makemigrations` and execute the migration via `python manage.py migrate`

After migration, we can then start server `python manage.py runserver` and register first user via POST request at endpoint `http://localhost:8000/api/auth/register/`.

```http
POST /api/auth/register/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
    "email": "test1@gmail.com",
    "password": "123456",
    "profile": {"display_name": "tester1", "first_name": "Hao", "last_name": "Hsueh"}
}
```

Then log in the user via POST request at endpoint `http://localhost:8000/api/auth/token/`

```http
POST /api/auth/token/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
    "email": "test1@gmail.com",
    "password": "123456"
}
```

You will then obtain one access token and one refresh token:

```json
{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyMDAyNTM0OCwiaWF0IjoxNzE5NzY2MTQ4LCJqdGkiOiJmOWZmOGZkZGM2OTg0OWUwOTYwNGQ3ZDI2YzVhY2UzYSIsInVzZXJfaWQiOjN9.yuG6IUE1zdJoHeP9DyQwkfLn17EywKM3J3KHYzclsBE",
"access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5NzY3MDQ4LCJpYXQiOjE3MTk3NjYxNDgsImp0aSI6IjRkZTdmZjc3MGE0YzQ2ZDJhZDJlMWM3MzQ3YmQxZGVkIiwidXNlcl9pZCI6M30.xKzwi84TleElaEPkQs4mehryuAcD3OkjaAQ2aAVoEkg"}
```

You can refresh the access token via POST request at endpoint `http://localhost:8000/api/auth/token/refresh/`.

```http
POST /api/auth/token/refresh/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyMDAyNTM0OCwiaWF0IjoxNzE5NzY2MTQ4LCJqdGkiOiJmOWZmOGZkZGM2OTg0OWUwOTYwNGQ3ZDI2YzVhY2UzYSIsInVzZXJfaWQiOjN9.yuG6IUE1zdJoHeP9DyQwkfLn17EywKM3J3KHYzclsBE"
}
```

You will then obtain a new access token.

```json
{"access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5NzY3NTQ2LCJpYXQiOjE3MTk3NjYxNDgsImp0aSI6IjY0YTIwZGY2YjRhOTRjNzA4MjFkNmNkYmU3MWRiNGI5IiwidXNlcl9pZCI6M30.SnQp4K3MvKRTmJOpdJGwXUwi7CyzMGGMy-MgHXiEpfc"}
```

Use returned access token (put `Bearer {access_token}` in `Authorization` of request header) to prove authentication for a protected test api `http://localhost:8000/api/auth/test-protected/`:

```http
GET /api/auth/test-protected/ HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5NzY3NTQ2LCJpYXQiOjE3MTk3NjYxNDgsImp0aSI6IjY0YTIwZGY2YjRhOTRjNzA4MjFkNmNkYmU3MWRiNGI5IiwidXNlcl9pZCI6M30.SnQp4K3MvKRTmJOpdJGwXUwi7CyzMGGMy-MgHXiEpfc
```

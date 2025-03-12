# Email Verification and Define user groups

## Email Verification

Email server configuration and email template setup.

Create two new endpoints: `api/auth/verify-email/<uuid:token>/` and `api/auth/resend-verification/`


Add following configurations in `setting.py`

```python
# backend/settings.py

# Email Configuration
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = ENV('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = ENV('EMAIL_PORT', default=587)
    EMAIL_USE_TLS = ENV('EMAIL_USE_TLS', default=True)
    EMAIL_HOST_USER = ENV('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = ENV('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = ENV('DEFAULT_FROM_EMAIL', default='Recipe App <noreply@example.com>')
FRONTEND_URL = ENV('FRONTEND_URL', default='http://localhost:5173')

# Template directory
TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'templates')]
```

Update env file `.env.docker.dev`

```plaintext
# Email settings
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=Recipe App <noreply@example.com>
FRONTEND_URL=http://localhost:5173
```

create email html template with following structure

```plaintext
backend/
├─ templates/
│  ├─ email/
│  │  ├─ verification_email.html
│  │  ├─ welcome_email.html
```

`templates/email/verification_email.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Verify Your Email Address</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .button {
            display: inline-block;
            background-color: #4CAF50;
            color: white !important;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }
        .footer {
            margin-top: 40px;
            font-size: 12px;
            text-align: center;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Verify Your Email Address</h1>
    </div>
    
    <p>Hello,</p>
    
    <p>Thank you for signing up for {{ site_name }}. To complete your registration, please verify your email address by clicking the button below:</p>
    
    <p style="text-align: center; margin: 30px 0;">
        <a href="{{ verification_url }}" class="button">Verify Email</a>
    </p>
    
    <p>Alternatively, you can copy and paste the following link into your browser:</p>
    <p>{{ verification_url }}</p>
    
    <p>If you did not sign up for an account, you can ignore this email.</p>
    
    <p>This verification link will expire in 48 hours.</p>
    
    <p>Best regards,<br>The {{ site_name }} Team</p>
    
    <div class="footer">
        <p>This is an automated message, please do not reply.</p>
    </div>
</body>
</html>

```

`templates/email/welcome_email.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Welcome to {{ site_name }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .button {
            display: inline-block;
            background-color: #4CAF50;
            color: white !important;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }
        .footer {
            margin-top: 40px;
            font-size: 12px;
            text-align: center;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Welcome to {{ site_name }}</h1>
    </div>
    
    <p>Hello,</p>
    
    <p>Thank you for verifying your email address. Your account is now fully activated!</p>
    
    <p>With your free account, you can browse recipes, apply basic filters, and explore our platform. When you're ready to access more features, consider upgrading to one of our subscription plans.</p>
    
    <p style="text-align: center; margin: 30px 0;">
        <a href="{{ login_url }}" class="button">Log In Now</a>
    </p>
    
    <p>Here are a few things you can do with your new account:</p>
    <ul>
        <li>Browse our collection of recipes</li>
        <li>Save your favorite recipes</li>
        <li>Use basic search functionality</li>
    </ul>
    
    <p>We hope you enjoy using {{ site_name }}!</p>
    
    <p>Best regards,<br>The {{ site_name }} Team</p>
    
    <div class="footer">
        <p>This is an automated message, please do not reply.</p>
    </div>
</body>
</html>

```

Adjust `UserManager` and  `User` model. Then create `EmailVerification` model

```python
# api_auth/models.py

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
        is_email_verified=False, # Add this line.
        tier='free'  # Add this line. Default tier for new users 
        **extra_fields
    )
    user.set_password(password)
    user.save(using=self._db)
    return user

    ...

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)  # Add this line
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
    
    # Add the "tier: field
    TIER_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]
    tier = models.CharField(
        max_length=10,
        choices=TIER_CHOICES,
        default='free'
    )
    
    ...


class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=2)  # Token valid for 2 days
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"Verification for {self.user.email}"

    class Meta:
        db_table = 'email_verification'
```

Update `CustomUserSerializer`. Then create `EmailVerificationSerializer` and `ResendVerificationSerializer`

```python
# api_auth/serializers.py

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_active', 'is_email_verified', 'is_staff', 
                  'last_login', 'date_joined', 'register_method', 'tier')

...

class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerification
        fields = ('token',)
        read_only_fields = ('token',)

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
```

Create a `utils.py` under `api_auth` directory. Then create email utility functions

```python
# api_auth/utils.py

import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

def send_verification_email(user, verification_token):
    """
    Send email verification link to the user
    """
    context = {
        'user': user,
        'verification_url': f"{settings.FRONTEND_URL}/verify-email/{verification_token}",
        'site_name': 'Recipe Subscription App',
    }
    
    html_content = render_to_string('email/verification_email.html', context)
    text_content = strip_tags(html_content)
    
    try:
        msg = EmailMultiAlternatives(
            subject='Verify Your Email Address',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_welcome_email(user):
    """
    Send welcome email after verification
    """
    context = {
        'user': user,
        'login_url': f"{settings.FRONTEND_URL}/login",
        'site_name': 'Recipe Subscription App',
    }
    
    html_content = render_to_string('email/welcome_email.html', context)
    text_content = strip_tags(html_content)
    
    try:
        msg = EmailMultiAlternatives(
            subject='Welcome to Recipe Subscription App',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False

```

Update `views.py`: update `CustomRegisterView`. Then create two new views `VerifyEmailView` and `ResendVerificationView`

```python

class CustomRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    
    # add this part
    def perform_create(self, serializer):
        user = serializer.save()
        # Create verification token
        verification = EmailVerification.objects.create(user=user)
        # Send verification email
        send_verification_email(user, verification.token)

...

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

```

> About VerifyEmailView method (GET vs PATCH):
>
>While PATCH would be more strictly RESTful (you're updating a resource), GET is the conventional and more practical choice for email verification because:
>
> * Users click a link in their email, which generates a GET request
> * GET requests are simpler to implement (no CSRF concerns)
> * It's the industry standard pattern that users are familiar with
> * Email clients may not support other HTTP methods in links

Update URLs

```python
# api_auth/urls.py

urlpatterns = [
    ...
    path('verify-email/<uuid:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
]


```

Start server:

```bash
python manage.py makemigrations api_auth
docker-compose -f docker-compose.dev.yml up --build 

```
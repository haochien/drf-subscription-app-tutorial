
# Simple JWT Setup

This project uses Django simplejwt as one of the authentication method.

## Set up Simple JWT in Django

### 1. install simple jwtv library

```sh
pip install djangorestframework-simplejwt
```

### 2. Update settings.py

Add `rest_framework_simplejwt` in `INSTALLED_APPS`

```python
# ./backend/settings.py

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
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
}

```

### 3. Create customized 
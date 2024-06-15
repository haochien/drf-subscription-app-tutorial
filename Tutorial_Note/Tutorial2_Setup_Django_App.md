## Create Django app

### 1. create first app in the project api_auth
```sh
cd .\backend\subscription_app\
python manage.py startapp api_auth
```

After the app is created, the folder structure will be:
```
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ api_auth/
│  ├─ subscription_app/
│  ├─ requirements.txt
├─ frontend/
├─ .gitignore
```

Add the new app to `INSTALLED_APPS` in `api_auth/settings.py`:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api_auth',  # Add the new app here
]
```
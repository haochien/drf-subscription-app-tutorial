## Create Django app

### 1. create first app in the project api_auth
```sh
cd .\backend\
python manage.py startapp api_auth
```

After the app is created, the folder structure will be:
```
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ api_auth/
│  ├─ backend/
│  ├─ manage.py
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


### 2. set up env file 
download django-environ
```sh
pip install django-environ

# export downloaded libraries to requirement.txt
pip freeze > .\backend\requirements.txt
```

Create a .env file in the root directory of the Django project:
```
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ api_auth/
│  ├─ backend/
│  ├─ manage.py
│  ├─ .env
│  ├─ requirements.txt
├─ frontend/
├─ .gitignore
```


# Create Django app

## create first app in the project api_auth

```sh
cd .\backend\
python manage.py startapp api_auth
```

After the app is created, the folder structure will be:

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ api_auth/
│  ├─ backend/
│  ├─ manage.py
│  ├─ requirements.txt
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

## set up env file

download `django-environ`

```sh
pip install django-environ==0.11.2

# export downloaded libraries to requirement.txt
pip freeze > .\backend\requirements.txt
```

Create a `.env` file in the root directory of the Django project:

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ api_auth/
│  ├─ backend/
│  ├─ manage.py
│  ├─ .env
│  ├─ requirements.txt
├─ .gitignore
```

Then move some of private information or environment-based information from `setting.py` to `.env`:

```env
# .env

DEBUG=True
SECRET_KEY=your-secret-key
```

Export environment variable `DRF_ENV_FILE_NAME` to the system.

This path can let the django project get the .env file from correct path based on the environment (dev or production).

```sh
# windows
set DRF_ENV_FILE_NAME=.env

# linux
export DRF_ENV_FILE_NAME=.env

# If you have .env.prod for production environment, then do the following in production system:
set DRF_ENV_FILE_NAME=.env.prod
```

In dev environment, .env file will anyway in the default location `BASE_DIR / '.env'`.

Thus, even `DRF_ENV_FILE_NAME` is not defined in the system, the django project can still run without issue.

```python
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# export DRF_ENV_FILE_NAME to environment while deploy to production environment
ENV_FILE_NAME = os.getenv('DRF_ENV_FILE_NAME', '.env')
ENV_PATH = BASE_DIR / ENV_FILE_NAME

# Initialize environment variables
ENV = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(BASE_DIR / '.env')


SECRET_KEY = ENV('SECRET_KEY')

DEBUG = ENV('DEBUG')
```

## Set up Django Rest Framework in the project

### 1. Add rest_framework into the `INSTALLED_APPS` in `settings.py`

```python
# backend/settings.py

INSTALLED_APPS = [
    ...
    'rest_framework',
    'api_auth',
]
```

### 2. Create a test Model

```python
# api_auth/model.py

class TestModel(models.Model):
    test_id = models.AutoField(primary_key=True)
    display_name = models.CharField(max_length=20)
    test_count = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField (default=1)

    def __str__(self):
        return str(self.display_name)
    
    class Meta:
        db_table = 'test_model'  # This will create a table named 'test_model'
```

### 2. Create a Serializer

Create a serializer for the model in the serializers.py file.

```python
# api_auth/serializers.py

from rest_framework import serializers
from .models import TestModel

class TestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        fields = '__all__'

```

### 3. Create a View

```python
# api_auth/view.py

from django.shortcuts import render
from rest_framework import viewsets
from .models import TestModel
from .serializers import TestModelSerializer

class TestModelViewSet(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer
```

### 4. Configure URLs

Create a urls.py file in the api_auth app.

```python
# api_auth/url.py

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
```

```python
# backend/url.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('api_auth.urls')),
]
```

>Q&A:
>
>**1. what is the usage of DefaultRouter()**:
>
> DefaultRouter() is a way to simply the following codes
>
> ```python
> # api_auth/url.py
>
> urlpatterns = [
>     path('test/', views.TestModelViewSet.as_view({ 'get': 'list', 'post': 'create'})),
>     path('test/<int:pk>/', views.TestModelViewSet.as_view({ 'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
> ]
> ```
>
> with DefaultRouter(), the same url configuration can be achieved by simpler codes.
> Via `/api/auth/test/`, you can create or fetch all data.
> Via `/api/auth/test/1`, you can fetch, update, or delete the selected data (i.e. here the target is pk=1)
>

### 5. Run Migrations

Create and apply the database migrations for your new model.

```sh
python manage.py makemigrations
python manage.py migrate
```

### 6. Start server and test api

start the server

```sh
cd .\backend
python manage.py runserver
```

Then try `http://127.0.0.1:8000/api/auth/test/` to get all or create new data.
Or `http://127.0.0.1:8000/api/auth/test/1` to get, udpate, delete the created data (replace 1 by any existed pk)

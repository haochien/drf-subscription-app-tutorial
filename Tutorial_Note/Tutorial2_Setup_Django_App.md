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

## set up env file

download `django-environ`

```sh
pip install django-environ

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
├─ frontend/
├─ .gitignore
```

Then move some of private information or environment-based information from `setting.py` to `.env`:

```plaintext
# .env

DEBUG=True
SECRET_KEY=your-secret-key
```

```python
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(BASE_DIR / '.env')


SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG')
```

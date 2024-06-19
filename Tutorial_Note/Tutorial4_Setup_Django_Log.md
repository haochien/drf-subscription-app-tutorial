# Set up log in Django

## Configure Logging

### 1. Set up path of log file in `.env` file

create a folder `logs` under django project main folder.
(will explain how to automize this process later on)

```plaintext
drf-subscription-app-Tutorial/
├─ local_db/
├─ backend/
│  ├─ logs
│  ├─ manage.py
├─ frontend/
```

Then set up environment variable for the log path

```env
# .env

# log file name
LOG_FILE_NAME=debug.log

# log folder name
LOG_FILE_FOLDER=logs
```

### 2. Configure Logging in `settings.py`

Add a `LOGGING` dictionary to your `settings.py file`. This dictionary will define the logging configuration, including loggers, handlers, and formatters.

```python
LOG_FILE_PATH = os.path.join(BASE_DIR, ENV('LOG_FILE_FOLDER'), ENV('LOG_FILE_NAME'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(levelname)-5s %(filename)s:%(lineno)-12s %(message)s',
        },
        'file': {
            'format': '%(asctime)-2s %(levelname)-5s %(thread)s %(name)-5s %(filename)s:%(lineno)-12s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_FILE_PATH,
            'when': 'midnight', # 's': Seconds ; 'M': Minutes ; 'H': Hours ; 'D': Days
            'interval': 1,
            'backupCount': 5,
            'formatter': 'file',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

> Tips:
>
> You can restructure or add more log message formatting in the `formatters`.
>
> In the example, two types of formatting were created `console` and `file`
>
> The `loggers` part defines loggers for different parts of the application
>
> In the `handlers` part, two different log handlers are used. `StreamHandler` is for the logging in console, and `TimedRotatingFileHandler` is to generate log file in everyday midnight.
>
> There are way more different handler options, such as `RotatingFileHandler`, `SMTPHandler`, `SysLogHandler`, ...etc.
>

### 3. Optional: automatically create logger folder

In the step 1, we created a `logs` folder manually.

If this folder was not created (i.e. directory does not exist), then the logger configuration will raise an error.

However, this step can be automized.

Everytime when the server starts, we can check whether the `logs` folder exists or not. If it does not exist, then we automatically create it.

#### a. Create a folder auto generation function

Delete the `logs` folder we created in the step 1.

Create a new pyhton script `server_start.py` under `.\backend\backend`.

```plaintext
drf-subscription-app-Tutorial/
├─ local_db/
├─ backend/
│  ├─ backend
│  │  ├─ settings.py
│  │  ├─ server_startup.py
├─ frontend/
```

```python
# .\backend\backend\server_startup.py

from django.conf import settings
import os

env = settings.ENV

def init_log_path():
    log_file_path = os.path.join(env('LOG_FILE_FOLDER'), env('LOG_FILE_NAME'))
    if not (os.path.exists(env('LOG_FILE_FOLDER'))):
        os.makedirs(env('LOG_FILE_FOLDER'))
        open(log_file_path, 'w').close()

    return log_file_path
```

#### b. update `settings.py`

Then import `init_log_path` and update `LOG_FILE_PATH` in `settings.py`

```python
# .\backend\backend\setting.py

# export DRF_ENV_PATH to environment while deploy to production environment
ENV_PATH = os.getenv('DRF_ENV_PATH', BASE_DIR / '.env')

# Initialize environment variables
ENV = environ.Env(
    DEBUG=(bool, False)
)

# init_log_path has to be imported after ENV line
from .server_startup import init_log_path
LOG_FILE_PATH = init_log_path()
# LOG_FILE_PATH = os.path.join(BASE_DIR, ENV('LOG_FILE_FOLDER'), ENV('LOG_FILE_NAME'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

}
```

## Test Logging

### 1. update `TestModelViewSet` in `api_auth\views.py`

```python
from django.shortcuts import render
from rest_framework import viewsets
from .models import TestModel
from .serializers import TestModelSerializer
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class TestModelViewSet(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer

    def list(self, request, *args, **kwargs):
        logger.info('TestModelViewSet list view called')
        logger.warning('Warning log in list view')
        return super().list(request, *args, **kwargs)
```

### 2. start server and check logs

start server via the command below

```sh
python manage.py runserver
```

After server starts, the `logs` file and `debug.log` will automatically created.

go `http://127.0.0.1:8000/api/auth/test/` and you will see the log information is documented into the `debug.log` and also displays in the console.

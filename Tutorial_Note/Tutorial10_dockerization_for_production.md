# Containerization for production environment

The Django development server (runserver) is NOT suitable for production because:

1. **Performance**: It's single-threaded and can only handle one request at a time
2. **Security**: Not designed to face the internet directly, lacks security hardening
3. **Features**: Lacks production features, like Worker process management, Request queuing, Load balancing, Security headers, and SSL/TLS handling

We need additional `WSGI` (Web Server Gateway Interface) and `Web Server` when deploy the Django app to the production environment.

## Gunicorn and Nginx

### 1. Why Gunicorn

Gunicorn is a WSGI (Web Server Gateway Interface) server that:

1. **Handles Python Processing**:

    * Runs multiple worker processes to handle concurrent requests
    * Each worker runs your Django application
    * Manages process lifecycle (starts/stops/restarts workers)

2. **Performance Benefits**:

    * Can handle multiple requests simultaneously
    * Memory management and leak prevention
    * Load balancing between workers

3. **Production Features**:

    * Request queuing
    * Health checks
    * Error handling

### 2. Why Nginx

A web server (like Nginx) sits in front of Gunicorn and:

1. **Static File Handling**:

    * Efficiently serves static files (images, CSS, JavaScript)
    * Reduces load on Python processes
    * Provides caching

2. **Security Features**:

    * SSL/TLS termination
    * DDoS protection
    * Request rate limiting
    * IP filtering

3. **Additional Features**:

    * Compression (gzip/brotli)
    * Load balancing
    * Reverse proxy
    * URL rewriting

### 3. Setup

1. **Development Setup** `Client → Django Development Server`:

    * Single-threaded
    * No security features
    * Poor performance
    * No static file optimization

2. **Minimal Production Setup** `Client → Gunicorn → Django`:

    * Inefficient static file serving
    * Limited security features
    * No SSL handling
    * No compression

3. **Recommended Production Setup** `Client → Nginx → Gunicorn → Django`:

    * Efficient static file handling
    * Optimal performance
    * Proper security

`Nginx`: Handles HTTP(S), static files, and security. Nginx is optimized for serving static content and handling connections.

`Gunicorn`: Handles Python processing and application logic. Gunicorn is optimized for running Python applications.

```plaintext
Internet Request
       ↓
    Nginx
  (Port 80/443)
       ↓
   - Handles SSL
   - Serves static files
   - Security checks
       ↓
   Gunicorn
  (Internal port)
       ↓
   - Process management
   - Python execution
       ↓
Django Application
```

## Set up Gunicorn

### 0. install gunicorn library to python environment

Add Gunicorn to the requirements.txt. We will need this to start server via gunicorn

```plaintext
gunicorn==21.2.0
```

### 1. create Gunicorn configuration file

create `gunicorn.conf.py` in the backend directory.

``` bash
# Number of worker processes
workers = 3

# The socket to bind
bind = "0.0.0.0:8000"

# Timeout for worker processes
timeout = 120

# Maximum number of pending connections
backlog = 2048

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# worker type (sync or async)
# worker_class = 'gevent'

# Keep-alive connection timeout
# keepalive = 65
```

#### a. workers

Determines how many worker processes Gunicorn will spawn. Each worker can handle one request at a time.

Common formula is `(2 x CPU cores) + 1`

Example with 2 CPU cores: Core 1: Can handle 2 workers efficiently; Core 2: Can handle 2 workers efficiently;  there will be 1 buffer worker for new requests while others are busy

Having too many workers will waste memory and cause CPU thrashing (too much context switching)

#### b. Socket Binding

Specifies the network interface and port Gunicorn listens on.

`0.0.0.0`: Listen on all available network interfaces

`8000`: Port number

#### c. Timeout

Maximum time (in seconds) a worker can take to handle a request. Default is 30 seconds.

Increase for long-running operations. For example: Quick APIs (timeout = 30), Default web apps (timeout = 60), File processing (timeout = 300)

Timeouts prevent blocked workers from hanging indefinitely, memory leaks from long-running processes, and single slow requests from affecting other users

#### d. Backlog

Maximum number of pending connections. Queues connections when all workers are busy. Default is 2048

Increase for high-traffic sites. For example: Low traffic (backlog = 1024), High traffic (backlog = 4096)

When backlog is full, new connections are rejected and clients get "Connection Refused" error.

If backlog is 2048 and all 2048 connections waiting, total memory for backlog will be around 16MB (Memory per connection is around 8KB)

#### e. Maximum Requests and Jitter

`max_requests`: Number of requests a worker handles before restarting

`max_requests_jitter`: Random variation added to max_requests

Why needed: Prevents memory leaks by periodic worker restart

How it works: Worker starts → Handles requests → Memory grows slightly → After max_requests → Worker restarts → Memory freed

Increase for stable applications. For example: Stable app (max_requests = 2000), Memory issues (max_requests = 500), More randomness (max_requests_jitter = 100)

#### f. Logging

This part is  configured logging behavior.

`accesslog`: Log of all requests. `'-'`  means logging to stdout/stderr (good for Docker). We can also define a path to log to a specific file (e.g. `/var/log/gunicorn/access.log`)

`errorlog`: Log of errors and warnings

`loglevel`: Detail level of logging. Available log levels are: `debug`, `info`, `warning`, `error`, and `critical`

#### g. Worker type

`Sync` (default):  One request = One worker blocked. Good for development environment (simple, easy to debug)

`Gevent`: Async I/O: Handles multiple requests per worker. Better for I/O bound applications (most web apps)

#### h. Keep-alive connection timeout

Keeps HTTP connection open for subsequent requests. It reduces overhead of creating new connections and improves performance for multiple requests from same client.

Why 65 seconds: Standard client timeout = 60 seconds. Extra 5 seconds ensures server keeps connection (longer than client expects)

How it works:

```plaintext
Without keepalive:
Request 1 → New connection → Process → Close
Request 2 → New connection → Process → Close

With keepalive:
Request 1 → New connection → Process → Keep open
Request 2 → Use existing connection → Process
Result: Faster response, less overhead
```

### 2. (Optional) include the development static file

To properly show the correct styling of Django Admin or Django Rest Framework UI, we need to collect all static file into one folder.

There is one step have to be done:

* update `settings.py`: we need to define `STATIC_ROOT`. This will later be the place we collect all static files across the apps in our Django project.

    ```python
    STATIC_URL = 'static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    ```

Combing with `python manage.py collectstatic` command we will prepare in the next step, the incorrect Django UI styling issue can be solved.

If adding this does not solve the styling issue, consider to add following as well:

* update `backend/urls.py`:

    ```python
    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('api/auth/', include('api_auth.urls')),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    ```

Further details of this fix can be checked here:

* [Django Rest Framework - Missing Static Directory](https://stackoverflow.com/questions/25375448/django-rest-framework-missing-static-directory)
* [Django application (runs in docker container) does not load static files](https://forum.djangoproject.com/t/django-application-runs-in-docker-container-does-not-load-static-files/22138)

This step is optional since we only need to call the api in our DRF. No static file will be requested and we don't need to use DRF UI and Django Admin UI in production.

### 3. create startup script `entrypoint.sh`

Create `entrypoint.sh` in the backend directory

Before starting server, there are a few command should be done. We include them all in this `entrypoint.sh`.

```bash
#!/bin/sh

# Validate environment variables
if [ -z "$DATABASE_HOST" ] || [ -z "$DATABASE_PORT" ]; then
    echo "Error: Database environment variables not set"
    exit 1
fi

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
max_retries=30
retry_count=0
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
    retry_count=$((retry_count+1))
    if [ $retry_count -gt $max_retries ]; then
        echo "Error: PostgreSQL not available after ${max_retries} retries"
        exit 1
    fi
    sleep 0.1
done
echo "PostgreSQL started"

# Collect static files (Optional)
echo "Collecting static files..."
if ! python manage.py collectstatic --noinput; then
    echo "Error: Static file collection failed"
    exit 1
fi

# Run migrations
echo "Running migrations..."
if ! python manage.py migrate; then
    echo "Error: Database migration failed"
    exit 1
fi

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn backend.wsgi:application -c gunicorn.conf.py
```

#### a. Validate environment variables

This is a shell condition that checks if environment variables are empty or unset.

```bash
# Variable is unset
DATABASE_HOST=
[ -z "$DATABASE_HOST" ]  # Returns trues

# Variable has value
DATABASE_HOST=localhost
[ -z "$DATABASE_HOST" ]  # Returns false
```

#### b. Wait for PostgreSQL to be ready

Ensures PostgreSQL is ready before starting the application.

`nc -z`: Tests connection to PostgreSQL. `-z` means "zero-I/O mode" or "scanning mode". It only checks if the port is open, without sending any data and establishing a full connection

We add a maximum try to prevent infinite loop.

#### c. Collect static files

This step will gathers all static files from different locations into a single directory specified by STATIC_ROOT (defined in settings.py), including Django/DRF development static file.

```plaintext
Before collectstatic:
/app1/static/css/style.css
/app2/static/js/script.js
/lib/static/images/logo.png

After collectstatic:
/staticfiles/css/style.css
/staticfiles/js/script.js
/staticfiles/images/logo.png
```

`--noinput`: tells Django to run the command without asking for user confirmation.

If you don't run collectstatic:

1. Development server: Works fine (Django serves static files automatically)
2. Production server: Static files won't work because: Gunicorn doesn't serve static files, and Nginx/Apache needs all static files in one location

However, this step is optional. It is the same reason as the step 2 above

#### d. Run migrations

This step is required before run django server. It applies data model changes to the database

#### e. Start Gunicorn

This will start the production web server

`exec`: Replaces shell process with Gunicorn

`backend.wsgi:application`: Path to WSGI application (Make sure `backend.wsgi` matches your project structure)

`-c gunicorn.conf.py`: Configuration file path

### 4. Update `Dockerfile`

We need to adjust Dockerfile to able to run server by Gunicorn.

``` dockerfile
# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copy project
COPY . .

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
```

Explanation on updates:

#### a. Install system dependencies

This step installs required system packages

`apt-get update`: Updates package list

`--no-install-recommends`: Minimizes installed packages

`netcat-traditional`: For database health checks

`rm -rf /var/lib/apt/lists/*`: Cleans up to reduce image size. `/var/lib/apt/lists/` contains package lists downloaded by `apt-get` update. These lists are only needed during package installation. Removing them reduces Docker image size

#### b. Copy entrypoint script

This step copies and makes entrypoint script executable.

`chmod +x`: Change mode (permissions) and add eXecutable permission

>Tips:
>
>You can check file/directory permission by, for example, `-rw-r--r--` or `drwxr-xr-x`
>
>```plaintext
>First character (Position 0):
>- : Regular file
>d : Directory
>l : Symbolic link
>
>Next 9 characters are divided into 3 groups of 3:
>
>rwxr-xr-x
>[rwx][r-x][r-x]
> ↓    ↓    ↓
>user group others
>
>Each group can have:
>r: Read permission
>w: Write permission
>x: Execute permission
>-: No permission
>
>drwxr-xr-x  images/
>user   : can read, write, and execute for directory images/
>group  : can read and execute for directory images/
>others : can read and execute for directory images/
>```
>
>We can change the permission by:
>
>```plaintext
>chmod u+x file    # Add execute for user
>chmod g+w file    # Add write for group
>chmod o-r file    # Remove read for others
>```

#### c. Run entrypoint script

Specifies the command to run when container starts

### 5. Start server

The final backend folder should look like this:

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ api_auth/
│  ├─ backend/
│  ├─ .dockerignore
│  ├─ Dockerfile
│  ├─ docker-compose.yml
│  ├─ manage.py
│  ├─ requirements.txt
│  ├─ .env.docker
│  ├─ gunicorn.conf.py
│  ├─ entrypoint.sh
├─ frontend
├─ .gitignore
```

After all these changes, run cd to backend folder and run `docker-compose up --build` to start the server!

# Containerization (for dev environment)

In the previous tutorial, we have covered how to set up and run django in the local environment.

however, it will be quite complicated and challenge to prepare all these set up and dependency for different local environment and even for the future deployment.

Putting all the dependency and setup in a container would be then a good solution for this topic.

In this tutorial, we will create docker files and include all those set up in the container and run in a virtual machine.

This tutorial will cover the dockerization of backend part and database part for development environment (in the later chapter, we will cover the setup for production environment).

## Prepare Docker files

### 1. create a Dockerfile

Create a Dockerfile in the backend directory.

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ backend/
│  ├─ Dockerfile.dev
│  ├─ manage.py
│  ├─ requirements.txt
│  ├─ .env
├─ .gitignore
```

```dockerfile
# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project to virtual machine working directory
COPY . .
```

#### a. Use Python 3.12 slim image

In the first step `FROM python:3.12-slim`, we select python 3.12 version as our base image.

`slim` is a minimized version of the Python image. It is smaller than full Python image and contains only essential packages.

#### b. Set environment variables

`PYTHONDONTWRITEBYTECODE=1`: Prevents Python from writing .pyc files (compiled bytecode). This can reduces container size.

`PYTHONUNBUFFERED=1`: Forces Python to run in unbuffered mode. Output is sent straight to terminal without buffering. This can prevent delays in seeing Python output in Docker logs.

#### c. Set work directory

Creates and sets the working directory in the container. All subsequent commands will run from this directory.

`WORKDIR /app` would be similar to running `mkdir /app` && `cd /app`

#### d. Install Python dependencie

`COPY requirements.txt .`: copy requirements.txt from current location /backend to the working directory in the container (i.e. /app)

`pip install --upgrade pip`: Updates pip to latest version. Ensures compatibility and security updates.

`pip install --no-cache-dir -r requirements.txt`: Installs Python packages listed in requirements.txt.

With `--no-cache-dir`, it will not cache downloaded packages, reducing image size.

#### e. Copy project to virtual machine working directory

`COPY . .`: Copies all files from build context to container.

First `.` is the source in local directory (/backend). Second `.` is the destination (/app, due to `WORKDIR`)

Note that we will later create a `.dockerignore` to exclude certain files to be copied in this step.

>Hint:
>
>Why make an additional copy step for requirement.txt before copy all files `COPY . .`?
>
>This is actually a good practice for development environment.
>
>During development, codes are changed frequently and the image needs to be rebuild everytime when codes changed.
>
>If we do following:
>
>```dockerfile
>COPY . .
>RUN pip install --no-cache-dir -r requirements.txt
>```
>
>Every file is copied in one layer and Docker sees the layer changed. It will then reinstalled dependencies EVERY time (Build takes several minutes each time)
>
> with following approach:
>
>```dockerfile
>COPY requirements.txt .
>RUN pip install --no-cache-dir -r requirements.txt
>COPY . .
>```
>
>We take the advantage of Docker layer caching.
>
>If only codes are changed and requirements.txt is not changed, requirements.txt layer is then cached (unchanged), and pip install layer is also cached (unchanged)
>
>Only the final COPY is executed. Build takes only seconds

### 2. prepare docker env file

In the second step, we need to prepare another environment variable files for Docker to build the container.

The content of the new env file will be very similar to what we have created in `.env`. Only a few lines will be updated to match the later docker setup.

Create a `.env.docker.dev` in the backend directory.

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ backend/
│  ├─ Dockerfile
│  ├─ docker-compose.yml
│  ├─ manage.py
│  ├─ requirements.txt
│  ├─ .env
│  ├─ .env.docker.dev
├─ .gitignore
```

The copy the content from .env file to .env.docker. The env.docker will look like followings:

```env
# .env.docker.dev

DEBUG=True
SECRET_KEY=my-secret-key

# Django Database Settings
DATABASE_NAME=drf_subscription_app
DATABASE_USER=root
DATABASE_PASSWORD=secret
DATABASE_HOST=db
DATABASE_PORT=5432

# PostgreSQL Container Settings
POSTGRES_DB=${DATABASE_NAME}
POSTGRES_USER=${DATABASE_USER}
POSTGRES_PASSWORD=${DATABASE_PASSWORD}

LOG_FILE_NAME=debug.log
LOG_FILE_FOLDER=logs
```

There are two updates here:

1. change value of `DATABASE_HOST` from `localhost` to `db`:

    In Docker, services run in separate containers. If we keep `DATABASE_HOST` as `localhost`, database connection will fail because PostgreSQL isn't running on localhost inside the Django container

    In the next step, we will create a docker-compose.yml including database container as "db".

    Thus, we need DATABASE_HOST=db in the env file to use Docker's internal DNS

2. add PostgreSQL connection information:

    In the tutorial of Setup_Django_DB, we have created a docker-compose.yml to run the PostgreSQL locally.

    Instead of directly exposing our DB connection information in docker-compose file, we will now bring those private information into our .env.docker.dev.

    Thus, we also need the environment variable for `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`.

    Since we have define those three information already in `DATABASE_NAME`, `DATABASE_USER`, and `DATABASE_PASSWORD` of Django Database Settings part, we can reutilize these 3 variables for the PostgreSQL variables with:

    ```env
    POSTGRES_DB=${DATABASE_NAME}
    POSTGRES_USER=${DATABASE_USER}
    POSTGRES_PASSWORD=${DATABASE_PASSWORD}
    ```

### 3. create a docker-compose.yml

Create a `docker-compose.dev.yml` in the backend directory.

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ backend/
│  ├─ Dockerfile
│  ├─ docker-compose.dev.yml
│  ├─ manage.py
│  ├─ requirements.txt
│  ├─ .env
│  ├─ .env.docker.dev
├─ .gitignore
```

```yaml
version: '3.8'

services:
  web:
    container_name: subs_app_dev_web
    build:
      context: .
      dockerfile: Dockerfile.dev
    image: subs_app_dev_web:latest
    command: >
      bash -c "
        python manage.py migrate &&
        python manage.py runserver 0.0.0.0:8000
      "
    volumes:
      - .:/app
    # environment:
    #   - DRF_ENV_FILE_NAME=.env.docker.dev
    ports:
      - "8000:8000"
    env_file:
      - .env.docker.dev
    depends_on:
      - db
  db:
    container_name: subs_app_dev_db
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - .env.docker.dev
    ports:
      - "5432:5432" 

volumes:
  postgres_data:
    name: subs_app_dev_postgres_data

```

This file cover the setup for Python and PostgreSQL.

#### a. overall structure introduction

`version: '3.8'`： Specify Docker Compose file format version and determine available configuration options

`services:`: Defines the different services/containers in the application. Each service runs in a separate container but they can communicate with each other on an internal network.

`web:`: Defines the c service (you can change `web` to whatever name you want). Name 'web' is used as hostname in Docker's internal DNS and other services can refer to it as 'web'.

`db:`: Defines PostgreSQL database service. Name 'db' should match DATABASE_HOST in Django settings (you also can change `db` to whatever name you want. But, remember to also adjust your `DATABASE_HOST` in .env.docker.dev)

`volumes: postgres_data:`: Declares named volume for PostgreSQL data.

>Hint:
>
>What is Volumes?
>
> Volumes are folders on your host machine hard drive mounted (mapped) into containers
>
> use case: you try to store something in the file system from the programs, but the data will be gone once you delete the container. Volume can solve this.
>
> Container can write and read data to/from volumes

#### b. Django web application part - `web`

`container_name: subs_app_dev_web`: here we define the container name after it is created

`build:`: Tells Docker to build image from Dockerfile. `context: .` means Dockerfile is in current directory . `dockerfile: Dockerfile.dev` defined the file name of the Dockerfile.

`image: subs_app_dev_web:latest`: here we defined the image name after it is built

`command: > bash -c`: Command to run when container starts. We will run command in bash. 

`python manage.py migrate`: this will migrate django models to your DB

`python manage.py runserver 0.0.0.0:8000`: this is the command to start the dev server. `0.0.0.0` means listening on all network interfaces and `:8000` is the port Django runs on.

This setup is just for development server only (not for production).

>Hint:
>
>Why 0.0.0.0:8000? Why not 127.0.0.1:8000?
>
>127.0.0.1 (localhost) only accepts connections from the same machine (i.e. only accepts connections from inside the container)
>
>It won't be accessible from your host machine (your computer) and other containers

`volumes: - .:/app`: Mounts current directory to /app in container

It enables live code updates without rebuilding (Source code changes reflect immediately). `.` is the host directory (your local files). `/app` is container directory (where code runs)

`ports: - "8000:8000"`: Map the container port to the port on your machine (HOST_PORT:CONTAINER_PORT).

This will allow us to access Django app from browser.

In case there is any port conflict (e.g. you have run another Django app on your local machine at port 8000), you can change the left side port number (first 8000) to another number

`env_file: - .env.docker.dev`: Loads environment variables from .env.docker.dev, and variables will be available to the Django application

It is more secure to keep all sensitive data in env file, instead of directly listing the required variables in `environment:` section.

`depends_on: - db`: Ensures 'db' service starts before 'web' (This only waits for container to start, not for service to be ready)

#### c. PostgreSQL database service part - `db`

`image: postgres:15-alpine`: Uses official PostgreSQL 15 Alpine image. Alpine-based for smaller size

`volumes: - postgres_data:/var/lib/postgresql/data/`: Named volume for database persistence. `postgres_data`: Volume name defined in the end of the file. `/var/lib/postgresql/data/`: PostgreSQL data directory (Fixed path where PostgreSQL expects its data, determined by the PostgreSQL Docker image).

With volume set up, data survives container restarts/removals

`env_file: - .env.docker.dev`: Loads environment variables from .env.docker.dev. Since we define Django and PostgreSQL variables in one env file, here we load the same env file as `web` service

`ports: - "5432:5432"`: Exposes PostgreSQL port to host.

Since we would like to connect to DB via our local machine to really see the data inside (e.g. via GUI, such as TablePlus or pgAdmin), we need to expose the port.

If you don't want to connect to this DB via your local machine, it is totally fine to ignore this line.

Without expose port, `web` service can still reach database at `db:5432`

### 3. create .dockerignore

We don't want to copy some system files or sensitive files to our container.

In this case, we can use .dockerignore to tell Docker not to copy certain files in the `COPY` stage.

```.dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env*
*.sqlite3
.git
.gitignore
.vscode/
*.log
media/
static/
```

In our set up, we properly excluded the env files to be builded in the image. This will keep the sensitive data safe.

In final, you can start dev server by: `docker-compose -f docker-compose.dev.yml up --build`.
You can remove all container, images, volumns from this docker-compose file by: `docker-compose -f docker-compose.dev.yml down -v --rmi all`

>Hint:
>
>There might be a little bit confusion on the environment variable setup. Followings are the env configuration in Django settings.py:
>
>```python
>BASE_DIR = Path(__file__).resolve().parent.parent
>
>ENV_FILE_NAME = os.getenv('DRF_ENV_FILE_NAME', '.env')
>ENV_PATH = BASE_DIR / ENV_FILE_NAME
>
># Initialize environment variables
>ENV = environ.Env(
>    DEBUG=(bool, False)
>)
>
>environ.Env.read_env(ENV_PATH)
>```
>
>In our local machine setup, we read the environment variables from .env file. Thus we need to define `ENV_FILE_NAME` and `ENV_PATH`.
>
>via set up environment variable `DRF_ENV_FILE_NAME` in the system, Django can then know which env file to load.
>
>However, in Docker container, we don't want to copy env file into image due to security reason.
>
>We directly define `.env.docker` in `env_file`, so that all our environment variables have been loaded while container set up.
>
>Environment variables have a specific loading order/precedence (from highest to lowest priority):
>
>1. Runtime environment variables (set by Docker or the OS)
>2. Values in docker-compose.yml's environment section
>3. Variables from files specified in docker-compose.yml's env_file
>4. Variables loaded by django-environ from the .env file
>5. Default values in the code
>
>django-environ (ENV()) checks these sources also in such order.
>
>Since the value is found in the OS environment (thanks to Docker's env_file), it never needs to read from the .env file.
>
>And therefore, even though we don't define `DRF_ENV_FILE_NAME` and don't copy any env file in image building stage, django-environ can still get all required variables loaded from docker-compose.yml's env_file.
>
>Simple test:
>
>```python
># setting.py
>
>print(ENV_FILE_NAME)
>print(ENV_PATH)
>print(ENV('DATABASE_HOST'))
>
># results:
># ENV_FILE_NAME: .env (DRF_ENV_FILE_NAME cannot be found, using default value .env)
># ENV_PATH: /app/.env
># ENV('DATABASE_HOST'): db
>```
>
>If now we include `DRF_ENV_FILE_NAME` variable in docker-compose.yml and don't load the env variables from .env.docker.dev in built stage:
>
>```yml
>  web:
>    build: .
>    command: python manage.py runserver 0.0.0.0:8000
>    volumes:
>      - .:/app
>    ports:
>      - 8000:8000
>    environment:
>      - DRF_ENV_FILE_NAME=.env.docker.dev
>    #env_file:
>    #  - .env.docker.dev
>    depends_on:
>      - db
>```
>
>Also, we need to remove .env.docker from .dockerignore, so that .env.docker can be copied into container for later django-environ to read.
>
>In this case, if we run the same test again, you will see the result as followings:
>
>```python
># setting.py
>
>print(ENV_FILE_NAME)
>print(ENV_PATH)
>print(ENV('DATABASE_HOST'))
>
># results:
># ENV_FILE_NAME: .env.docker.dev (the variable DRF_ENV_FILE_NAME is found)
># ENV_PATH: /app/.env.docker.dev
># ENV('DATABASE_HOST'): db
>```
>
>As you can see, two approaches loaded environment variables in different stage. But the results are identical
>
>Since excluding env file from container is more secured way, approach 1 is then recommended.

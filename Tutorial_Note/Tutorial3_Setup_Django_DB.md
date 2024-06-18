# Set up PostgreSQL DB in Django

## create PostgreSQL DB for dev environment

Followings are several ways you can set up PostgreSQL DB.
In this tutorial, the method of Docker Setup will be used.

### 1. Local Setup

#### a. Install PostgreSQL Locally

* Windows: Download the installer from the PostgreSQL website.
* macOS: Use Homebrew with the command brew install postgresql.
* Linux: Use your package manager, for example, sudo apt-get install postgresql for Debian-based systems.

#### b. Create a PostgreSQL Database

```sh
# Access the PostgreSQL prompt
psql -U postgres
# Create a new database
CREATE DATABASE drf_subscription_app;
# Create a new user
CREATE USER root WITH PASSWORD 'secret';
# Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE drf_subscription_app TO root;
```

### 2. Docker Setup

Using Docker is a convenient way to run PostgreSQL locally without installing it directly on your machine.

#### a. Create a Docker Container for PostgreSQL

Download Docker via [Docker website](https://www.docker.com/products/docker-desktop/)

Check whether download is successful via following commands:

```sh
docker --version
docker-compose --version
```

Then create a docker-compose.yml file in your project directory.
In this tutorial, we create a local_db folder and put ymal file inside it

```plaintext
drf-subscription-app-Tutorial/
├─ local_db/
│  ├─ docker-compose.yml
├─ backend/
├─ frontend/
├─ .gitignore
```

```yml
# docker-compose.yml

services:
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=drf_subscription_app
    ports:
      - "5432:5432"
```

use following command to start the db:

```sh
cd .\local_db
docker-compose up -d

# check whether the container of the PostgreSQL DB is active
docker ps

# if you want to shut down the container
docker-compose down
```

### 3. Cloud Setup

For a more flexible and scalable solution, consider using a cloud provider:

#### a. Amazon RDS

* Create a PostgreSQL instance using the Amazon RDS console.
* Follow the instructions to configure your database and get the connection details.

#### b. Google Cloud SQL

* Create a PostgreSQL instance in the Google Cloud Console.
* Configure the database and get the connection details.

> Tips:
>
> Once the DB server up, you can use GUI tool to interacte with your PostgreSQL DB, e.g. pgAdmin, TablePlus.
>
> For more choices, you can read this [article](https://www.datensen.com/blog/postgresql/top-5-gui-tools-for-postgresql/)
>

## Configure Django to Use PostgreSQL

### 1. Install `psycopg2`

You need the psycopg2 package to connect Django to PostgreSQL.

```sh
pip install psycopg2-binary
```

### 2. Update `settings.py`

Put the DB connection information into the `.env` file

```env
DATABASE_NAME=drf_subscription_app
DATABASE_USER=root
DATABASE_PASSWORD=secret
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

Configure the database settings in your Django project's `settings.py` file.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST', default='localhost'),
        'PORT': env('DATABASE_PORT', default=5432),
    }
}

```

### 3. Migrate model to the PostgreSQL DB

```sh
python manage.py makemigrations # not required if no model change happened
python manage.py migrate
```

start server and check whether the api post successfully creates the data in DB.

```sh
cd .\backend
python manage.py runserver
```

Then try `http://127.0.0.1:8000/api/auth/test/` to create new data.

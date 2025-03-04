# Project Tree view

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ api_auth/
│  │  ├─ __init__.py
│  │  ├─ apps.py
│  │  ├─ models.py
│  │  ├─ serializers.py
│  │  ├─ signals.py
│  │  ├─ urls.py
│  │  ├─ views.py
│  ├─ backend/
│  │  ├─ __init__.py
│  │  ├─ asgi.py
│  │  ├─ wsgi.py
│  │  ├─ settings.py
│  │  ├─ server_startup.py
│  │  ├─ urls.py
│  ├─ nginx/
│  │  ├─ Dockerfile.nginx.digitalocean
│  │  ├─ Dockerfile.nginx.digitalocean.ssl
│  │  ├─ Dockerfile.nginx.prod
│  │  ├─ nginx.digitalocean.conf
│  │  ├─ nginx.digitalocean.ssl.conf
│  │  ├─ nginx.prod.conf
│  ├─ scripts/
│  │  ├─ deploy.sh
│  │  ├─ get-cert.sh
│  │  ├─ setup-server.sh
│  ├─ .env.docker.dev
│  ├─ .env.docker.prod
│  ├─ .env.docker.digitalocean
│  ├─ .env
│  ├─ .deploy.sh
│  ├─ gunicorn.conf.py
│  ├─ entrypoint.sh
│  ├─ .dockerignore
│  ├─ Dockerfile.dev
│  ├─ Dockerfile.prod
│  ├─ docker-compose.dev.yml
│  ├─ docker-compose.prod.yml
│  ├─ docker-compose.digitalocean.yml
│  ├─ docker-compose.digitalocean.ssl.yml
│  ├─ manage.py
│  ├─ requirement.txt
├─ frontend/
│  ├─ public/
│  ├─ src/
│  │  ├─ assets/
│  │  ├─ components/
│  │  │  ├─ AuthForm.jsx
│  │  │  ├─ AuthForm.module.css
│  │  │  ├─ GoogleLoginButton.jsx
│  │  │  ├─ ProtectedRoute.jsx
│  │  ├─ pages/
│  │  │  ├─ Home.jsx
│  │  │  ├─ Login.jsx
│  │  │  ├─ LoginGoogleCallBack.jsx
│  │  │  ├─ TestAPI.jsx
│  │  │  ├─ TestDemo.jsx
│  │  ├─ utils/
│  │  │  ├─ auth.js
│  │  ├─ App.jsx
│  │  ├─ api.js
│  │  ├─ constant.js
│  │  ├─ main.jsx
│  │  ├─ theme.js
│  ├─ .env
│  ├─ postcss.config.cjs
│  ├─ package.json
│  ├─ index.html
│  ├─ .eslintrc.cjs
│  ├─ package.json
│  ├─ vite.config.js
├─ local_db/
│  ├─ docker-compose.yml
├─ .gitignore
├─ .vscode/
│  ├─ launch.json
```

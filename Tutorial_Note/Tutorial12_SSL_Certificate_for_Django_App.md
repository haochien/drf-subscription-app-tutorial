# SSL Certificate for Django App

In this tutorial, we focus on how to secure a containerized Django app running behind an HTTPS Nginx proxy with Let's Encrypt SSL certificates.

After setup, your app will be able to be connected via HTTPS.  In addition, all HTTP connection will be redirected to HTTPS.

This setup uses:

* `Docker containers` for service isolation
* `Nginx` as a reverse proxy
* `Certbot` to obtain and renew SSL certificates from Let's Encrypt
* `Django/Gunicorn` as the application server

## Configure Your Domain DNS

SSL certificates are tied to domain names, not IP addresses, because:

* Domain names are human-readable and memorable
* One IP might host multiple domains (virtual hosting)
* SSL validates the identity of a domain, not just encrypting traffic
* Most Certificate Authorities (CAs) won't issue certs for raw IPs

Follow steps below to set up a domain name for your Droplet IP:

1. Set up an A record for your domain (e.g., my-website.com) pointing to your Droplet's IP address

2. Wait for DNS propagation (can take up to 24-48 hours, but often much quicker)

3. Verify with: `dig my-website.com +short` (your Droplet's IP should return if set up correctly)

You can buy domain by any domain registrars For example, Namecheap and Cloudflare.

Here we use Cloudflare as an example:

For DNS configuration:

1. Log into your Cloudflare account
2. If you don't have any domain yet, use `+ Add a domain` button to purchase your domain
3. If you have a domain in Cloudflare, select your domain in Account Home.
4. At `Go to...` search box, search DNS
5. Create a `A record` (i.e. Tyep A) which pointed to IPv4 address if your Droplet
6. Make sure Proxy status is switch to `DNS only` (the cloud icon is GRAY (not orange))

## Set Up Directory Structure in your Droplet

In your Droplet, create directories to store SSL certificates:

```bash
mkdir -p /root/drf-subscription-app-tutorial/data/certbot/www/.well-known/acme-challenge/
mkdir -p /root/drf-subscription-app-tutorial/data/certbot/conf
chmod -R 755 /root/drf-subscription-app-tutorial/data
```

however, we don't want `/data/certbot/` directory under our git control.

In the `.gitignore`, we need to add the following entry:

```.gitignore
# certbot relevant directory
/data/certbot/
```

## Create Nginx Configuration for SSL

### 1. Set up a new nginx conf

Create a new file `nginx.digitalocean.ssl.conf` with contents below under `/backend/nginx` directory:

Please replace all 5 `my-website.com` in the script below to your real domain name

```nginxconf
upstream django_backend {
    server web:8000;
}

# HTTP - redirect all requests to HTTPS except for certbot challenge
server {
    listen 80;
    listen [::]:80;

    server_name my-website.com;
    server_tokens off;
    
    # Required for Let's Encrypt certificate enrollment
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS - proxy all requests to Django
server {
    listen 443 ssl;
    server_name my-website.com;
    server_tokens off;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/my-website.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/my-website.com/privkey.pem;
    
    # SSL parameters
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;
    
    # SSL session parameters
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/my-website.com/chain.pem;
    resolver 1.1.1.1 8.8.8.8 valid=60s;
    resolver_timeout 5s;

    location / {
        proxy_pass http://django_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        client_max_body_size 20M;
    }

    location /static/ {
        alias /app/staticfiles/;
    }
}

```

### 2. Set up a new nginx Dockerfile

Create a new file `Dockerfile.nginx.digitalocean.ssl` with contents below under `/backend/nginx` directory:

```Dockerfile
FROM nginx:1.25-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom config
COPY nginx.digitalocean.ssl.conf /etc/nginx/conf.d/default.conf
```

## Update Docker Compose Configuration

Create a new file `docker-compose.digitalocean.ssl.yml` with contents below under `/backend` directory:

```yml

version: '3.8'

services:
  web:
    container_name: subs_app_prod_web
    build:
      context: .
      dockerfile: Dockerfile.prod
    image: subs_app_prod_web:latest
    volumes:
      - static_volume:/app/staticfiles
      - logs_volume:/app/logs
    env_file:
      - .env.docker.digitalocean
    expose:
      - 8000
    restart: unless-stopped
  
  nginx:
    container_name: subs_app_prod_nginx
    build:
      context: ./nginx
      dockerfile: Dockerfile.nginx.digitalocean.ssl
    image: subs_app_prod_nginx:latest
    volumes:
      - static_volume:/app/staticfiles
      - logs_volume:/app/logs
      - ../data/certbot/conf:/etc/letsencrypt
      - ../data/certbot/www:/var/www/certbot
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    command: "/bin/sh -c 'while :; do sleep 6h & wait $${!}; nginx -s reload; done & nginx -g \"daemon off;\"'"
    restart: unless-stopped
  
  certbot:
    image: certbot/certbot
    container_name: subs_app_prod_certbot
    volumes:
      - ../data/certbot/conf:/etc/letsencrypt
      - ../data/certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    restart: unless-stopped

volumes:
  static_volume:
    name: subs_app_prod_static_files
  logs_volume:
    name: subs_app_prod_logs

```

## Create Certificate Acquisition Script

Create a new file `get-cert.sh` with contents below under `/backend/scripts` directory.

Please keep the content as followings. We will change Domain and Email later directly in the Droplet.

```bash
#!/bin/bash

DOMAIN=my-website.com  # Replace with your domain
EMAIL=your-email@example.com  # Replace with your email
STAGING=1  # Set to 0 for production, 1 for staging

# Stop any running services that might use port 80
docker compose -f docker-compose.digitalocean.ssl.yml stop nginx

# Determine the correct Let's Encrypt server URL
if [ "$STAGING" -eq 1 ]; then
  SERVER_URL="https://acme-staging-v02.api.letsencrypt.org/directory"
  echo "Running in STAGING mode - certificates will NOT be trusted by browsers"
else
  SERVER_URL="https://acme-v02.api.letsencrypt.org/directory"
  echo "Running in PRODUCTION mode - certificates will be trusted by browsers"
fi

# Remove any previous certificates to start fresh
rm -rf /root/drf-subscription-app-tutorial/data/certbot/conf/live/*
rm -rf /root/drf-subscription-app-tutorial/data/certbot/conf/archive/*
rm -rf /root/drf-subscription-app-tutorial/data/certbot/conf/renewal/*
rm -rf /root/drf-subscription-app-tutorial/data/certbot/conf/accounts/

# Obtain a new certificate from Let's Encrypt's production server
docker run --rm \
  -v "/root/drf-subscription-app-tutorial/data/certbot/conf:/etc/letsencrypt" \
  -v "/root/drf-subscription-app-tutorial/data/certbot/www:/var/www/certbot" \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  -d $DOMAIN \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  --force-renewal \
  --server $SERVER_URL

# Verify the certificate
docker run --rm \
  -v "/root/drf-subscription-app-tutorial/data/certbot/conf:/etc/letsencrypt" \
  certbot/certbot certificates

# Start nginx and other services
docker compose -f docker-compose.digitalocean.ssl.yml up -d
```

## Obtain SSL Certificate and Start Services

Push all changes above to your Github

ssh to your droplet and follow the steps below

```bash

ssh root@your-droplet-ip

# remove existed containers
cd /root/drf-subscription-app-tutorial/backend
docker compose -f docker-compose.digitalocean.ssl.yml down

# pull latest changes
cd /root/drf-subscription-app-tutorial
git pull origin main

# build images based on latest changes
cd /root/drf-subscription-app-tutorial/backend
docker compose -f docker-compose.digitalocean.ssl.yml build --no-cache

# update get-cert.sh
vi /root/drf-subscription-app-tutorial/backend/scripts/get-cert.sh
# press i to go into insert mode 
# update values in DOMAIN and EMAIL (due to rate limit, please keep STAGING=1 in testing)
# press Esc, and type :wq to save


# execute get-cert.sh
chmod +x /root/drf-subscription-app-tutorial/backend/scripts/get-cert.sh
cd /root/drf-subscription-app-tutorial/backend
./scripts/get-cert.sh
```

## Test connection

Verify your HTTPS setup via:

```bash
curl -v https://my-website.com
```

If everything set up correctly, you should see:

```plaintext
* Connected to my-website.com (your-droplet-ip) port 443 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
*  CAfile: /etc/ssl/certs/ca-certificates.crt
*  CApath: /etc/ssl/certs
* TLSv1.0 (OUT), TLS header, Certificate Status (22):
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.2 (IN), TLS header, Certificate Status (22):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.2 (IN), TLS header, Finished (20):
* TLSv1.2 (IN), TLS header, Supplemental data (23):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.2 (IN), TLS header, Supplemental data (23):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.2 (OUT), TLS header, Unknown (21):
* TLSv1.3 (OUT), TLS alert, unknown CA (560):
* SSL certificate problem: unable to get local issuer certificate
* Closing connection 0
curl: (60) SSL certificate problem: unable to get local issuer certificate
More details here: https://curl.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the web page mentioned above.
```

You can also check that your site is accessible in a web browser (e.g. https://my-website.com/api/auth/test/)

you will also see a certificate warning in your browser.

The reason for the SSL certificate problem above is that our certificate is still using Let's Encrypt's staging environment which is why browsers and curl don't trust it.

We need to do followings to get the certificate from Let's Encrypt's production environment:

```bash
ssh root@your-droplet-ip

# update get-cert.sh
vi /root/drf-subscription-app-tutorial/backend/scripts/get-cert.sh
# press i to go into insert mode 
# update values in STAGING to production mode (i.e. STAGING=0)
# press Esc, and type :wq to save

# execute again get-cert.sh
./scripts/get-cert.sh
```

Now you will see:

```plaintext
* Connected to my-website.com (your-droplet-ip) port 443 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
*  CAfile: /etc/ssl/certs/ca-certificates.crt
*  CApath: /etc/ssl/certs
* TLSv1.0 (OUT), TLS header, Certificate Status (22):
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.2 (IN), TLS header, Certificate Status (22):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.2 (IN), TLS header, Finished (20):
* TLSv1.2 (IN), TLS header, Supplemental data (23):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.2 (IN), TLS header, Supplemental data (23):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.2 (IN), TLS header, Supplemental data (23):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.2 (IN), TLS header, Supplemental data (23):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.2 (OUT), TLS header, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.2 (OUT), TLS header, Supplemental data (23):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
* ALPN, server accepted to use http/1.1
* Server certificate:
*  subject: CN=bmy-website.com
*  start date: Mar  2 10:59:24 2024 GMT
*  expire date: May 31 10:59:23 2024 GMT
*  subjectAltName: host "my-website.com" matched cert's "my-website.com"
*  issuer: C=US; O=Let's Encrypt; CN=E6
*  SSL certificate verify ok.
```

And when you check your site via a web browser (e.g. https://my-website.com/api/auth/test/), you should also see no warning and can directly use this test api in DRF UI
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

## Update env file and Django settings.py

### 1. ENV file

make sure you add your domain in ALLOWED_HOSTS

```plaintext
ALLOWED_HOSTS=my-website.com,46.101.220.14
```

### 2. settings.py

Add following part in `settings.py`

```python

# SSL setting
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```


## Set Up Directory Structure in your Droplet

In your Droplet, create directories to store SSL certificates:

```bash
mkdir -p /root/drf-subscription-app-tutorial/data/certbot/www/.well-known/acme-challenge/
mkdir -p /root/drf-subscription-app-tutorial/data/certbot/conf
chmod -R 755 /root/drf-subscription-app-tutorial/data
```

The folder in your droplet would looks like

```plaintext

drf-subscription-app-tutorial/
├─ backend/
│  ├─ scripts/
│  ├─ nginx/
│  ├─ docker-compose.digitalocean.yml
│  ├─ ...
├─ data/
│  ├─ certbot/
│  │  ├─ conf/  (mapped to /etc/letsencrypt in containers)
│  │  ├─ www/   (mapped to /var/www/certbot in containers)

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

* HTTP Server Block: Handles HTTP requests on port 80
  * Redirects all traffic to HTTPS except for Let's Encrypt challenge requests
  * Serves .well-known/acme-challenge/ for certificate validation

* HTTPS Server Block: Handles HTTPS requests on port 443
  * Configures SSL with modern TLS protocols and strong ciphers
  * Proxies requests to the Django application
  * Serves static files

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
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew --webroot --webroot-path=/var/www/certbot --quiet; sleep 12h & wait $${!}; done;'"
    restart: unless-stopped

volumes:
  static_volume:
    name: subs_app_prod_static_files
  logs_volume:
    name: subs_app_prod_logs

```

Services:

* Web Service: our Django application with Gunicorn
* Nginx Service: Reverse proxy with SSL termination
* Certbot Service: Automatic certificate renewal

Volume Mounts:

* static_volume: Django static files
* logs_volume: Application logs
* certbot/conf: Let's Encrypt certificates and configuration
* certbot/www: Webroot for Let's Encrypt challenges

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
  STAGING_FLAG="--staging"
  echo "Running in STAGING mode - certificates will NOT be trusted by browsers"
else
  STAGING_FLAG=""
  echo "Running in PRODUCTION mode - certificates will be trusted by browsers"
fi

# Remove any previous certificates to start fresh
rm -rf /root/drf-subscription-app-tutorial/data/certbot/conf/live/*
rm -rf /root/drf-subscription-app-tutorial/data/certbot/conf/archive/*
rm -rf /root/drf-subscription-app-tutorial/data/certbot/conf/renewal/*
rm -rf /root/drf-subscription-app-tutorial/data/certbot/conf/accounts/


# Start a temporary Nginx for webroot authentication
docker run --rm -d --name temp-nginx \
  -v "/root/drf-subscription-app-tutorial/data/certbot/www:/usr/share/nginx/html" \
  -p 80:80 \
  nginx:alpine

# Give Nginx a moment to start
sleep 2

# Obtain a new certificate using webroot
docker run --rm \
  -v "/root/drf-subscription-app-tutorial/data/certbot/conf:/etc/letsencrypt" \
  -v "/root/drf-subscription-app-tutorial/data/certbot/www:/var/www/certbot" \
  certbot/certbot certonly --webroot -w /var/www/certbot \
  -d $DOMAIN \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  --force-renewal \
  $STAGING_FLAG

# Stop temporary Nginx
docker stop temp-nginx

# Verify the certificate
docker run --rm \
  -v "/root/drf-subscription-app-tutorial/data/certbot/conf:/etc/letsencrypt" \
  certbot/certbot certificates

# Start nginx and other services
docker compose -f docker-compose.digitalocean.ssl.yml up -d
```

Besides using staging flag, you can also directly define the server to get staging certificate or production certificate.

```bash
# Determine the correct Let's Encrypt server URL
if [ "$STAGING" -eq 1 ]; then
  SERVER_URL="https://acme-staging-v02.api.letsencrypt.org/directory"
  echo "Running in STAGING mode - certificates will NOT be trusted by browsers"
else
  SERVER_URL="https://acme-v02.api.letsencrypt.org/directory"
  echo "Running in PRODUCTION mode - certificates will be trusted by browsers"
fi

#....

# Obtain a new certificate using webroot
docker run --rm \
  -v "/root/drf-subscription-app-tutorial/data/certbot/conf:/etc/letsencrypt" \
  -v "/root/drf-subscription-app-tutorial/data/certbot/www:/var/www/certbot" \
  certbot/certbot certonly --webroot -w /var/www/certbot \
  -d $DOMAIN \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  --force-renewal \
  --server $SERVER_URL

```

In case you have problem on getting initial certificate (maybe due to different nginx setup), you can try to use standalone approach in `get-cert.sh`.

Once you can get the initial certificate, you can switch back to webroot approach and debug why only standalone approach works.

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


# Obtain a new certificate using standalone approach
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

You can see followings for the details on these two approaches.

> **Standalone vs. Webroot: Let's Encrypt Certificate Approaches**
>
> 1. Differences Between Approaches:
>
>       Standalone Mode
>
>       * How it works: Certbot spins up its own temporary web server on port 80
>       * Requirements: Port 80 must be free (requires stopping your Nginx)
>       * Simplicity: Simpler to configure initially
>       * Downtime: Requires stopping any existing web server
>
>       Webroot Mode
>
>       * How it works: Uses your existing web server to serve ACME challenge files
>       * Requirements: Your web server must be properly configured to serve files from the certbot webroot
>       * Complexity: Slightly more complex initial setup
>       * Downtime: No downtime needed, works alongside your running web server
>
> 2. When to Use Each Approach
>
>       Use Standalone When:
>
>       * Setting up certificates for the first time on a new server
>       * Troubleshooting certificate issues
>       * Working in development environments
>       * Your web server configuration is complex or problematic
>       * You can tolerate brief downtime during certificate operations
>
>       Use Webroot When:
>
>       * Running in production environments
>       * Continuous operation is required
>       * Automatic renewal needs to work without intervention
>       * Your web server is already properly configured
>       * You need zero-downtime certificate management
>
> 3. Best Practice for Production
>
>       The webroot approach is definitely the better choice for production environments because:
>
>       * Consistent Method: Using the same method for both initial acquisition and renewals ensures compatibility
>       * Zero Downtime: Certificates can be renewed without interrupting service
>       * Automation Friendly: Works seamlessly with automated renewal processes
>       * Standard Practice: It's the industry-standard approach for production systems

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

## Test certificate renew process

Let's Encrypt certificates operate with the following timeline:

* Certificates are valid for 90 days
* Automated renewal attempts typically start 30 days before expiration
* our container is configured to check every 12 hours (twice daily)

You can check your certificate status by `docker exec subs_app_prod_certbot certbot certificates`
To properly test that your automatic certificate renewal will work when needed, here are three methods:

### 1. Test Renewal with Dry Run

The most straightforward way to test the renewal process without actually affecting your certificates:

```bash
# Run a manual renewal simulation
docker exec subs_app_prod_certbot certbot renew --webroot --webroot-path=/var/www/certbot --dry-run

# A successful dry-run will show something like:
# Congratulations, all renewals succeeded. The following certs have been renewed:
#   /etc/letsencrypt/live/my-website.com/fullchain.pem (success)
```

If this works, your renewal configuration is correct.

### 2. Inspect Container Logs:

Check if the renewal attempts are being properly logged:

```bash
# Check if the container is running
docker ps | grep certbot

# Check the letsencrypt logs inside the container
docker exec subs_app_prod_certbot grep "renewal" /var/log/letsencrypt/letsencrypt.log

# You should see:
#DEBUG:certbot._internal.display.obj:Notifying user: Processing /etc/letsencrypt/renewal/my-website.com.conf
#DEBUG:certbot._internal.display.obj:Notifying user: Certificate not yet due for renewal
#DEBUG:certbot._internal.display.obj:Notifying user: The following certificates are not due for renewal yet:
#DEBUG:certbot._internal.display.obj:Notifying user: No renewals were attempted.
#DEBUG:certbot._internal.renewal:no renewal failures

```

You should see log entries showing renewal attempts every 12 hours.

### 3. Force Manual Renewal Test

Force a renewal to see if the complete renewal process works (including Nginx picking up new certificates):

```bash
# Force a renewal regardless of expiration date
docker exec subs_app_prod_certbot certbot renew --webroot --webroot-path=/var/www/certbot --force-renewal
```

After running this, wait a few minutes for Nginx's automatic reload cycle, then check if HTTPS is still working correctly:

```bash
curl -v https://my-website.com
```

## Other checking

In case you need to have a deeper look on how the config or certificate looks like, following commands might be helpful.

```bash
# check whether your config in container is correct
docker exec -it subs_app_prod_nginx cat /etc/nginx/conf.d/default.conf

# If you encounter permission issues with the certificate files, check:
docker exec -it subs_app_prod_nginx ls -la /etc/letsencrypt/live/my-website.com/

# Let's Encrypt uses symbolic links for certificates, so let's check that they're working properly:
docker exec -it subs_app_prod_nginx readlink -f /etc/letsencrypt/live/my-website.com/fullchain.pem
docker exec -it subs_app_prod_nginx readlink -f /etc/letsencrypt/live/my-website.com/privkey.pem
```

## DEBUGGING (Optional reading materials)

If you face issue on getting new certificate, we can break the process down into smaller and verifiable steps.

We need to break this down into smaller, verifiable steps:z

1. First, get Nginx running with a minimal configuration (HTTP only)
2. Verify the ACME challenge path (`.well-known/acme-challenge/`) is accessible
3. Once HTTP is working, obtain certificates with Certbot
4. Finally, enable HTTPS with the obtained certificates

### Step 1: Create a minimal HTTP-only Nginx configuration

update your nginx configuration `nginx.digitalocean.ssl.conf`

```nginxconf
upstream django_backend {
    server web:8000;
}

server {
    listen 80;
    listen [::]:80;

    server_name backendtest.haodevelop.com;
    server_tokens off;
    
    # Required for LE certificate enrollment
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://django_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_redirect off;
        client_max_body_size 20M;
    }

    location /static/ {
        alias /app/staticfiles/;
    }
}
```

Make sure your `Dockerfile.nginx.digitalocean.ssl` still copy from this config file.

```Dockerfile
FROM nginx:1.25-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom config
COPY nginx.digitalocean.ssl.conf /etc/nginx/conf.d/default.conf
```

### Step 2: Update docker-compose to use HTTP only

modify your docker-compose file to use this HTTP-only configuration:

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
      dockerfile: Dockerfile.nginx.digitalocean
    image: subs_app_prod_nginx:latest
    volumes:
      - static_volume:/app/staticfiles
      - logs_volume:/app/logs
      - ../data/certbot/www:/var/www/certbot
    ports:
      - "80:80"
    depends_on:
      - web
    restart: unless-stopped

volumes:
  static_volume:
    name: subs_app_prod_static_files
  logs_volume:
    name: subs_app_prod_logs
```

### Step 3: Create a test file for verification

Create a test file under `.well-known/acme-challenge`

```bash
mkdir -p /root/drf-subscription-app-tutorial/data/certbot/www/.well-known/acme-challenge/
echo "This is a test file" > /root/drf-subscription-app-tutorial/data/certbot/www/.well-known/acme-challenge/test.txt
chmod -R 755 /root/drf-subscription-app-tutorial/data
```

### Step 5: Check if Nginx is running and test the ACME challenge path

If this works and returns "This is a test file", we can proceed with obtaining the certificate.

```bash
docker ps
docker logs subs_app_prod_nginx
curl -v http://my-website.com/.well-known/acme-challenge/test.txt
```

### Step 6: Create a simple certbot script

update `get-cert.sh`:

```bash
#!/bin/bash

DOMAIN=my-website.com  # Replace with your domain
EMAIL=myemail@example.com  # Replace with your email
STAGING=0 # Set to 1 if you're testing your setup

# Create a temporaray certbot container to obtain the certificate
docker run --rm -it \
  -v "/root/drf-subscription-app-tutorial/data/certbot/conf:/etc/letsencrypt" \
  -v "/root/drf-subscription-app-tutorial/data/certbot/www:/var/www/certbot" \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d $DOMAIN \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  --force-renewal \
  --staging

echo "Certificate should now be obtained. Check the directory:"
ls -la /root/drf-subscription-app-tutorial/data/certbot/conf/live/
```

execute the script

```bash
chmod +x /root/drf-subscription-app-tutorial/backend/scripts/get-cert.sh
cd /root/drf-subscription-app-tutorial/backend
./scripts/get-cert.sh
```

### Step 8: Create the SSL Nginx configuration

If all steps above works and the certificate was obtained successfully, you should have no problem to get certificate and access the app via HTTPS via the approach we provided in the beginning of this tutorial.

Change `nginx.digitalocean.ssl.conf`, `get-cert.sh`, and `docker-compose.digitalocean.ssl.yml` back to original setup and run followings:

```bash
cd /root/drf-subscription-app-tutorial/backend
docker compose -f docker-compose.digitalocean.ssl.yml down
docker compose -f docker-compose.digitalocean.ssl.yml up -d --build
curl -v https://my-website.com
```

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
  --server $SERVER_URL


# Stop temporary Nginx
docker stop temp-nginx

# # Obtain a new certificate from Let's Encrypt's production server
# docker run --rm \
#   -v "/root/drf-subscription-app-tutorial/data/certbot/conf:/etc/letsencrypt" \
#   -v "/root/drf-subscription-app-tutorial/data/certbot/www:/var/www/certbot" \
#   -p 80:80 \
#   certbot/certbot certonly --standalone \
#   -d $DOMAIN \
#   --email $EMAIL \
#   --agree-tos \
#   --no-eff-email \
#   --force-renewal \
#   --server $SERVER_URL



# Verify the certificate
docker run --rm \
  -v "/root/drf-subscription-app-tutorial/data/certbot/conf:/etc/letsencrypt" \
  certbot/certbot certificates

# Start nginx and other services
docker compose -f docker-compose.digitalocean.ssl.yml up -d
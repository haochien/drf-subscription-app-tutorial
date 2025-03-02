#!/bin/bash

DOMAIN=my-website.com  # Replace with your domain
EMAIL=your-email@example.com  # Replace with your email

# Stop any running services that might use port 80
docker compose -f docker-compose.digitalocean.yml stop nginx

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
  --server https://acme-v02.api.letsencrypt.org/directory



# domains=(my-website.com)
# email="your-email@example.com"
# staging=0
# docker run --rm -it \
#   -v "/root/drf-subscription-app-tutorial/data/certbot/conf:/etc/letsencrypt" \
#   -v "/root/drf-subscription-app-tutorial/data/certbot/www:/var/www/certbot" \
#   certbot/certbot certonly --webroot \
#   -w /var/www/certbot \
#   ${staging:+"--staging"} \
#   --email $email \
#   --agree-tos \
#   --no-eff-email \
#   --force-renewal \
#   ${domains[@]/#/-d }


# Verify the certificate
docker run --rm \
  -v "/root/drf-subscription-app-tutorial/data/certbot/conf:/etc/letsencrypt" \
  certbot/certbot certificates

# Start nginx and other services
docker compose -f docker-compose.digitalocean.yml up -d
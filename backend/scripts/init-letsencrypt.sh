#!/bin/bash

domains=(example.org www.example.org)
rsa_key_size=4096
data_path="../data/certbot"
email="your-email@example.com" # Adding a valid address is strongly recommended
staging=0 # Set to 1 if you're testing your setup to avoid hitting request limits

# Create required directories
mkdir -p "$data_path/conf/live/$domains"
mkdir -p "$data_path/www"


# Start nginx container first to handle the challenge
echo "### Starting nginx container for HTTP challenge..."
docker compose -f docker-compose.digitalocean.yml up --force-recreate -d nginx
echo

# Wait for nginx to start
echo "### Waiting for nginx to start..."
sleep 5

# Check if nginx is running
if ! docker ps | grep -q subs_app_prod_nginx; then
  echo "Error: Nginx container is not running. Check the logs with: docker logs subs_app_prod_nginx"
  exit 1
fi

# Check if the .well-known directory is accessible
echo "### Testing challenge directory..."
mkdir -p "$data_path/www/.well-known/acme-challenge"
echo "test file" > "$data_path/www/.well-known/acme-challenge/test.txt"
curl -s http://backendtest.haodevelop.com/.well-known/acme-challenge/test.txt
echo

# Request Let's Encrypt certificate
echo "### Requesting Let's Encrypt certificate for ${domains[0]}..."
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

# Select appropriate email arg
case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

# Enable staging mode if needed
if [ $staging != "0" ]; then staging_arg="--staging"; fi

docker compose -f docker-compose.digitalocean.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot
echo

# Reload nginx to apply the new certificate
echo "### Reloading nginx to apply the new certificate..."
docker compose -f docker-compose.digitalocean.yml exec nginx nginx -s reload

echo "### Done! HTTPS should be working now."
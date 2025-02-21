#!/bin/bash

# Pull latest changes
git pull origin main

# make sure entrypoint.sh has execution permission after git pull
# chmod +x entrypoint.sh
# Verify permissions
# ls -l entrypoint.sh
# Should show something like: -rwxr-xr-x

# Build and deploy
docker compose -f docker-compose.digitalocean.yml down
docker compose -f docker-compose.digitalocean.yml build
docker compose -f docker-compose.digitalocean.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs
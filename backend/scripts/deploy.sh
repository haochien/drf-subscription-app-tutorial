#!/bin/bash

# Pull latest changes
git pull origin main

# Build and deploy
docker compose -f docker-compose.digitalocean.ssl.yml down
docker compose -f docker-compose.digitalocean.ssl.yml build
docker compose -f docker-compose.digitalocean.ssl.yml up -d

# Check logs
docker compose -f docker-compose.digitalocean.ssl.yml logs
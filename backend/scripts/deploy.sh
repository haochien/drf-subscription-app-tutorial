#!/bin/bash

# Change to the backend directory first
cd "$(dirname "$0")/.." || exit

# Pull latest changes (from project root)
cd .. && git pull origin main && cd backend

# Pull latest changes
git pull origin main

# Build and deploy
docker compose -f docker-compose.digitalocean.yml down
docker compose -f docker-compose.digitalocean.yml build
docker compose -f docker-compose.digitalocean.yml up -d

# Check logs
docker compose -f docker-compose.digitalocean.yml logs
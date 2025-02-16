#!/bin/bash

# Pull latest changes
git pull origin main

# Build and deploy
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs
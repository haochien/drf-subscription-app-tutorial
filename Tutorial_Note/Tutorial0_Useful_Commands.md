# Useful Commands

## Docker relevant

```bash

# List all containers (including stopped)
docker ps -a

# List all images
docker images

# List all volumes
docker volume ls

# Remove container
docker rm -f my_container

# Remove image
docker rmi my_image:latest

# Remove volume
docker volume rm my_volume

```

## Docker compose

```bash

docker-compose -f docker-compose.prod.yml up --build


# Remove containers, networks
docker-compose -f docker-compose.dev.yml down

# Remove containers, networks, volumes, and only local images
docker-compose -f docker-compose.dev.yml down -v --rmi local

# Remove containers, networks, volumes, and images
docker-compose -f docker-compose.dev.yml down -v --rmi all

# Remove everything and remove orphaned containers
docker-compose -f docker-compose.dev.yml down -v --rmi all --remove-orphans


```


## Frontend relevant

```bash
npm install

npm run dev

npm run build
npm run preview

```

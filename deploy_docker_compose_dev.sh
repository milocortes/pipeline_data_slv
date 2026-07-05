#!/bin/bash

# Carga las variables de ambiente definidas en el archivo .env-dev
source .env-dev

# Añadimos permisos adicionales al archivo /var/run/docker.sock
sudo chmod 666 /var/run/docker.sock

# Sobreescribe el archivo Docker compose base de Apache Airflow para agregar las rutas específicas de los microservicios.
docker compose --env-file  .env-dev -f ./official-airflow-docker-compose.yml -f ./services-docker-compose-dev.yml config > docker-compose-dev.yml

# Ejecuta archivo de Docker compose.
docker compose -f docker-compose-dev.yml up  -d --build --force-recreate


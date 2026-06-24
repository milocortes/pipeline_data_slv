#!/bin/bash
source .env-dev
docker compose --env-file  .env-dev -f ./official-airflow-docker-compose.yml -f ./services-docker-compose-dev.yml config > docker-compose-dev.yml
docker compose -f docker-compose-dev.yml up  -d --build --force-recreate


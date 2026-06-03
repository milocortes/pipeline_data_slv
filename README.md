# pipeline_data_slv

## Docker compose
Compose override Docker compose file:

```bash
docker compose -f ./official-airflow-docker-compose.yml -f ./services-docker-compose.yml config > docker-compose.yml
```

Or the Docker compose dev file:

```bash
docker compose --env-file  .env-dev -f ./official-airflow-docker-compose.yml -f ./services-docker-compose-dev.yml config > docker-compose-dev.yml
```

You can run it using docker-compose:

```bash
docker compose -f docker-compose.yml up  -d --build
```

Or the Docker compose dev file:

```bash
docker compose -f docker-compose-dev.yml up  -d --build
```

Wait for a few seconds and you should be able to access the examples at http://localhost:8080/.

To stop running containers, run the following command:

```bash
docker compose down -v
```

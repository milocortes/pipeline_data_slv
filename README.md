# pipeline_data_slv

## Docker compose
Compose override Docker compose file:

```bash
docker compose -f ./official-airflow-docker-compose.yml -f ./services-docker-compose.yml config > docker-compose.yml
```

You can run it using docker-compose:

```bash
docker compose up -d --build
```

Wait for a few seconds and you should be able to access the examples at http://localhost:8080/.

To stop running containers, run the following command:

```bash
docker compose down -v
```

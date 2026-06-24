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
docker compose -f docker-compose-dev.yml up  -d --build --force-recreate
```

Wait for a few seconds and you should be able to access the examples at http://localhost:8080/.

To stop running containers, run the following command:

```bash
docker compose down -v
```

# Airflow in Minikube

To run Apache Airflow on Minikube, use the Official Apache Airflow Helm Chart to deploy its core components. Minikube requires extra CPU and memory resources to handle Airflow's webserver, scheduler, and database backends smoothly.

Follow this step-by-step guide to get Airflow opperational on your local cluster.


## 1. Initialize Minikube with Extra Resources

Airflow is resource-heavy. Allocate at least 4 CPUs and 8GB of RAM.

```bash
minikube start --cpus 4 --memory 8192
```

## 2. Add and Update the Airflow Helm Repository

Use Helm to fetch the official repository maintained by the Apache Airflow community.

```bash
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow \
--timeout 20m0s \
--create-namespace \
--namespace airflow \
--debug --set apiServer.service.type=LoadBalancer -f /etc/helm/values/git-values.yaml --set postgresql.image.repository=postgres --set postgresql.image.tag=16 
```

## 3. Verify the Running Pods

Monitor the deployment until the webserver, scheduler, and PostgresSQL pods transition into a Running status

```bash
kubectl get pods -n airflow
```

## 4. Access the Airflow Web UI

Minikube isolates container networks from your local machine. Use port forwarding to bridge the connection to your local browser

```bash
kubectl port-forward svc/airflow-api-server 8080:8080 --namespace airflow
```

Open http://localhost:8080 in your browser. Use the default credentials admin for both the username and password to log in.

## 5. How to Sync your DAGs

To add your custom workflows, you can pick one two paths:

- Git-Sync : Pass a Git repository URL directly into your Helm chart parameters. The scheduler will automatically pull code changes from your remote repository.

## Define configuration and credentials

Create a ConfigMap for non-secret settings and a Secret for database credentials. 

```bash
kubectl --namespace airflow apply -f resources/config.yaml
kubectl --namespace airflow get configmap,secret
```

## 6. Build the Docker images

### Add persistent storage for RustFS
```bash 
kubectl --namespace airflow  apply -f resources/storage.yaml
```

### Deploy RustFS Storage
Deploy and verify the service:

```bash 
kubectl --namespace airflow  apply -f resources/rustfs.yaml
```

Open the application: Use minikube to do this: 

```bash
minikube --namespace airflow service rustfs --url
```

### Deploy Administrator Dashboard (streamlit_app)

```bash 
minikube image build -t streamlit_app:1.0.0 -f services/streamlit_app/Dockerfile-compose-k8s .
```

Deploy and verify the service:

```bash
kubectl --namespace airflow  apply -f resources/streamlit.yaml
kubectl --namespace airflow  rollout status deploy/streamlit
kubectl --namespace airflow get svc streamlit

```

Open the application: Use minikube to do this: 

```bash
minikube --namespace airflow service streamlit --url
```

### Build `models`

```bash 
minikube image build -t models:1.0.0 -f services/models/Dockerfile-compose-dev .
```

### Build `subnacional`

```bash 
minikube image build -t subnacional:1.0.0 -f services/subnacional/Dockerfile-compose-dev .
```
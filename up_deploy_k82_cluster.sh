#!/bin/bash
## Initialize Minikube with Extra Resources
# Airflow is resource-heavy. Allocate at least 4 CPUs and 8GB of RAM.
minikube start --cpus 8 --memory 8192

## Add and Update the Airflow Helm Repository
# Use Helm to fetch the official repository maintained by the Apache Airflow community.
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow \
--timeout 20m0s \
--create-namespace \
--namespace airflow \
--debug --set apiServer.service.type=LoadBalancer -f /etc/helm/values/git-values.yaml 

## Define configuration and credentials
# Create a ConfigMap for non-secret settings and a Secret for database credentials. 
kubectl --namespace airflow apply -f resources/config.yaml

## Build the Docker images

### Build Administrator Dashboard (streamlit_app)
minikube image build -t streamlit_app:1.0.0 -f services/streamlit_app/Dockerfile-compose-k8s .

### Build `models`
minikube image build -t models:1.0.0 -f services/models/Dockerfile-compose-dev .

### Build `subnacional` 
minikube image build -t subnacional:1.0.0 -f services/subnacional/Dockerfile-compose-dev .

## Deploy pods
### Deploy Administrator Dashboard (streamlit_app)
kubectl --namespace airflow  apply -f resources/streamlit.yaml

### Add persistent storage for RustFS 
kubectl --namespace airflow  apply -f resources/storage.yaml

### Deploy RustFS Storage
kubectl --namespace airflow  apply -f resources/rustfs.yaml

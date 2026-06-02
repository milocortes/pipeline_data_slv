#!/bin/bash
# General environment variables
export start_date="2012-01-01"
export LSIB="FAO/GAUL/2015/level0"
export BUCKET_NAME="pronostico"
export service_account_gee="geoespacial@pib-geoespacial.iam.gserviceaccount.com"
export gee_project="pib-geoespacial"

# Storage environment variables
export RUSTFS_DNS="localhost" # RustFS server URL
export RUSTFS_PORT="9000"
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="rustfsadmin"
export AWS_SECRET_ACCESS_KEY="rustfsadmin"
export allow_http='true' # Required for non-HTTPS endpoints

# Apache Airflow environment variables
export AIRFLOW_APISERVER_DOMAIN="http://localhost"
export AIRFLOW_APISERVER_PORT="8080"
export _AIRFLOW_WWW_USER_PASSWORD="airflow"
export _AIRFLOW_WWW_USER_USERNAME="airflow"

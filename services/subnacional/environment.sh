#!/bin/bash
# General environment variables
export start_date="2012-01-01"
export LSIB="FAO/GAUL/2015/level0"
export BUCKET_NAME="pronostico"
export service_account_gee="geoespacial@pib-geoespacial.iam.gserviceaccount.com"
export gee_project="pib-geoespacial"

# Storage environment variables
export AWS_ENDPOINT_URL='http://127.0.0.1:9000'  # RustFS server URL
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="rustfsadmin"
export AWS_SECRET_ACCESS_KEY="rustfsadmin"
export allow_http='true' # Required for non-HTTPS endpoints


#!/bin/bash
# General environment variables
export start_date="2012-01-01"
export LSIB="FAO/GAUL/2015/level0"
export BUCKET_NAME="pronostico"
export BUCKET_RESPALDO="respaldo"
export service_account_gee="geoespacial@pib-geoespacial.iam.gserviceaccount.com"
export gee_project="pib-geoespacial"

# Storage environment variables
export RUSTFS_DNS="localhost" # RustFS server URL
export RUSTFS_PORT="9000"
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="rustfsadmin"
export AWS_SECRET_ACCESS_KEY="rustfsadmin"
export allow_http='true' # Required for non-HTTPS endpoints
export S3_AWS_STORAGE='False'

# Google Sheets environment variables
#export GS_SPREADSHEET="insumos-tablero-pib"
export GS_SPREADSHEET="test_pronostico"

# API Keys environment variables
export GS_API_KEY_FILE="pronosticos-493700-56f57502ffb3.json" 


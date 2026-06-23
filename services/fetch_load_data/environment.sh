#!/bin/bash
# General environment variables
export start_date="2012-01-01"
export LSIB="FAO/GAUL/2015/level0"
#export BUCKET_NAME="pronostico"
export BUCKET_NAME="pronostico-pib-geoespacial-slv"
export service_account_gee="geoespacial@pib-geoespacial.iam.gserviceaccount.com"
export gee_project="pib-geoespacial"

# Storage environment variables
export RUSTFS_DNS="localhost" # RustFS server URL
export RUSTFS_PORT="9000"
#export AWS_REGION="us-east-1"
#export AWS_ACCESS_KEY_ID="rustfsadmin"
#export AWS_SECRET_ACCESS_KEY="rustfsadmin"
export allow_http='true' # Required for non-HTTPS endpoints
export S3_AWS_STORAGE='True'

# API Keys environment variables
export BLACKMARBLE="eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6Imhlcm1pbG9jZyIsImV4cCI6MTc4MDY4OTY4NSwiaWF0IjoxNzc1NTA1Njg1LCJpc3MiOiJodHRwczovL3Vycy5lYXJ0aGRhdGEubmFzYS5nb3YiLCJpZGVudGl0eV9wcm92aWRlciI6ImVkbF9vcHMiLCJhY3IiOiJlZGwiLCJhc3N1cmFuY2VfbGV2ZWwiOjN9.f6PQ4vBjdjaylrnrUZ9qNhCkT59iopV33cORhCCDaOYooYa3XfyX1U7K0g92klIeIWyXxE7Bxm-X-p6n6UZ15fENDNDHyFOLMqV-IUwDXyub1F7Yj7jlcJNmfh0aC6ULkB6Eb6cr-jz_x4zA92cYxo7-bM4h6cDEmxq-ZAxkP-BqSivDmzwFVWaXHfNbI_dwtRS330cDioN-M7-Ljqjha19xLNoD84cgKbi-aESoaoy7BwvLclBwJr1G78P6BkDSjScmYRxmzEERuYkNYVEufIAIY_6pZR20qjQpxivWzWrKyac7irvLM8YC8F5RA4S-FZH5XwWtn1cnj3mjj5jPxg"
export FRED="63618b15604349ff9b39c8de2bfbd59a"
export GEE_API_KEY_FILE="pib-geoespacial-3ba5fc82e62c.json" 


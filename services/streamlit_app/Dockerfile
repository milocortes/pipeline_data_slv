FROM astral/uv:python3.12-bookworm-slim

# Set environment variables
# General environment variables
ENV start_date="2012-01-01"
ENV LSIB="FAO/GAUL/2015/level0"
ENV BUCKET_NAME="pronostico"
ENV service_account_gee="geoespacial@pib-geoespacial.iam.gserviceaccount.com"
ENV gee_project="pib-geoespacial"

# Storage environment variables
ENV RUSTFS_DNS="127.0.0.1"
ENV RUSTFS_PORT="9000"
ENV AWS_ACCESS_KEY_ID="rustfsadmin"
ENV AWS_SECRET_ACCESS_KEY="rustfsadmin"
ENV allow_http='true' 

# Apache Airflow environment variables
ENV AIRFLOW_APISERVER_DOMAIN="http://localhost"
ENV AIRFLOW_APISERVER_PORT="8080"
ENV _AIRFLOW_WWW_USER_PASSWORD="airflow"
ENV _AIRFLOW_WWW_USER_USERNAME="airflow"

# Copiamos codebase
COPY ./cov_administrativas /cov_administrativas
COPY ./cov_geoespaciales /cov_geoespaciales
COPY ./cov_subnacional /cov_subnacional
COPY ./metadata /metadata
COPY ./pages /pages
COPY ./utils /utils

COPY ./streamlit_app.py /streamlit_app.py

# Sincronizamos el proyecto uv
COPY ./pyproject.toml /pyproject.toml
COPY ./.python-version /.python-version
RUN uv sync 

ENTRYPOINT ["uv", "run", "streamlit", "run", "streamlit_app.py", "--server.port", "8502"]
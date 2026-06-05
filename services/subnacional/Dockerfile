FROM astral/uv:python3.12-bookworm-slim

# Define the R version you want
ARG R_VERSION=4.2.2.20221110-2

## Copia configuración de Python
COPY ./config /config
COPY ./pyproject.toml /pyproject.toml
COPY ./uv.lock /uv.lock
COPY ./.python-version /.python-version
RUN uv sync 

## Instala R
# 2. Pin and install specific R components
# Note: You may need to add the CRAN repository first if the version isn't in default Debian repos
RUN apt-get update && apt-get install -y --no-install-recommends default-jre default-jdk\
    r-base-core=${R_VERSION} \
    r-base-dev=${R_VERSION} \
    r-recommended=${R_VERSION} \
    && rm -rf /var/lib/apt/lists/*
    
## The xlsx library in R requires Java Development Kit (JDK) as the package depends on rJava
RUN R CMD javareconf
## Instala dependencias de R
COPY ./R_config.R /R_config.R 
RUN Rscript R_config.R

## Copia programas de la ejecución de la tarea
COPY ./crea_pdata_bpvar.py /crea_pdata_bpvar.py 
COPY ./bpvars.R /bpvars.R
COPY ./envia_delta_lake.py /envia_delta_lake.py
COPY ./envia_gs.py /envia_gs.py
COPY ./utils /utils 

# Set environment variables
# General environment variables
ENV start_date="2012-01-01"
ENV LSIB="FAO/GAUL/2015/level0"
ENV BUCKET_NAME="pronostico"
ENV service_account_gee="geoespacial@pib-geoespacial.iam.gserviceaccount.com"
ENV gee_project="pib-geoespacial"

# Storage environment variables
ENV AWS_ENDPOINT_URL='http://127.0.0.1:9000'
ENV AWS_REGION="us-east-1"
ENV AWS_ACCESS_KEY_ID="rustfsadmin"
ENV AWS_SECRET_ACCESS_KEY="rustfsadmin"
ENV allow_http='true' 

# API Keys environment variables
ENV GS_API_KEY_FILE="pronosticos-493700-56f57502ffb3.json" 

## Ejecuta tarea
COPY ./run_subnacional.sh /run_subnacional.sh
RUN chmod +x run_subnacional.sh
ENTRYPOINT ["bash", "run_subnacional.sh"]


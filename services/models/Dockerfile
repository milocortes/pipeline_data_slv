FROM astral/uv:python3.12-bookworm-slim
COPY ./config /config
COPY ./utils /utils 
COPY ./pyproject.toml /pyproject.toml
COPY ./uv.lock /uv.lock
COPY ./.python-version /.python-version
COPY ./x13as /usr/bin/

# Ensure it has execution permissions
RUN chmod +x /usr/bin/x13as
RUN apt update
RUN apt install -y libgfortran5

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

# Copy task
COPY ./arimax_models_rev.py /arimax_models_rev.py
COPY ./ml_models.py /ml_models.py
RUN uv sync

#ENTRYPOINT ["uv", "run", "arimax_models_rev.py"]
#ENTRYPOINT ["/usr/bin/x13as"]
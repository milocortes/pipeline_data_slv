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
COPY ./arimax_models_rev.py /arimax_models_rev.py
COPY ./ml_models.py /ml_models.py
RUN uv sync 
#ENTRYPOINT ["uv", "run", "arimax_models_rev.py"]
#ENTRYPOINT ["/usr/bin/x13as"]
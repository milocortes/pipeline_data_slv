FROM astral/uv:python3.12-bookworm-slim
COPY ./config /config
COPY ./tasks /tasks 
COPY ./pyproject.toml /pyproject.toml
COPY ./uv.lock /uv.lock
COPY ./.python-version /.python-version
RUN uv sync 
ENTRYPOINT ["uv", "run", "tasks/gdp_us_const_trim.py"]
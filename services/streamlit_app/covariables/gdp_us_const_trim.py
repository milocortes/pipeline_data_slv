import tomllib
from pathlib import Path
import polars as pl 
import streamlit as st
import altair as alt

## Carga configuración
FP = Path(".")

## Carga configuración general
with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)


## Cargamos tabla
gdp_us_const_trim = pl.read_delta(
    f"s3://{config['BUCKET_NAME']}/gdp_us_const_trim",
    storage_options=storage_options,
)

ts_plot = alt.Chart(gdp_us_const_trim).mark_line().encode(
    x='datetime:T',
    y='gdp_us_const_trim:Q'
)


st.altair_chart(ts_plot, use_container_width=False)

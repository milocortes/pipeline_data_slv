import tomllib
from pathlib import Path
import polars as pl 
import streamlit as st
from typing import Dict


import altair as alt
import json 
from streamlit_echarts import st_pyecharts
import pyecharts.options as opts
from pyecharts.charts import Line, Bar

## Carga configuración
FP = Path(".")

## Carga configuración general
with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

## Carga Metadatos de Variables geoespaciales
with open(FP/"metadata"/"geoespacial"/"metadata_geoespacial.toml", "rb") as f:
    metadata = tomllib.load(f)

## Cargamos tablas 
geospatial_vars = ["evi_gee", "ndbi_gee", "ndvi_gee", "precip"]

geospatial_data = {
    geo : pl.read_delta(
    f"s3://{config['BUCKET_NAME']}/{geo}",
    storage_options=storage_options,
)
    for geo in geospatial_vars
}

## Función que crea la gráfica de serie de tiempo
def time_series_plot(data : Dict[str, pl.DataFrame], 
                     ts_var : str, 
                     metadata : None) -> None:
        
    data2plot = data.with_columns(
        pl.col(ts_var).round(3),
        pl.col("datetime").dt.year().cast(pl.Utf8) + "Q" + pl.col("datetime").dt.quarter().cast(pl.Utf8) # Ajustamos el trimestre
        ).to_numpy()

    linea = (
        Line()
        .add_xaxis(xaxis_data=[item[0] for item in data2plot])
        .add_yaxis(
            series_name="",
            y_axis=[item[1] for item in data2plot],
            yaxis_index=0,
            #is_smooth=True,
            is_symbol_show=False,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=metadata["variable"]),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),

            yaxis_opts=opts.AxisOpts(
                type_="value",
                name_location="start",
                min_=round(data.select(ts_var).min().item(), 2),
                max_=round(data.select(ts_var).max().item(), 2) ,
                is_scale=True,
                axistick_opts=opts.AxisTickOpts(is_inside=False),
            ),
         )
    )

    st.title(metadata["descripcion"])
    st_pyecharts(linea)

    st.markdown(
        f"""
        * **Frecuencia** : {metadata['frecuencia_actualizacion']} 
        * **Frecuencia de Actualización** : {metadata['frecuencia_actualizacion_delta']}
        * **Rezago** : {metadata['rezago_fecha_actual']}
        * **Fuente** : {metadata['fuente']}
        """
    )


## Funciones especificas a cada variable
def render_evi_gee():
    time_series_plot(geospatial_data["evi_gee"], "evi_gee", metadata["evi_gee"])

def render_ndbi_gee():
    time_series_plot(geospatial_data["ndbi_gee"], "ndbi_gee", metadata["ndbi_gee"])

def render_ndvi_gee():
    time_series_plot(geospatial_data["ndvi_gee"], "ndvi_gee", metadata["ndvi_gee"])

def render_precip():
    time_series_plot(geospatial_data["precip"], "precip", metadata["precip"])

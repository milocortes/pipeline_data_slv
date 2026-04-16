import tomllib
from pathlib import Path
import polars as pl 

from utils import load_delta_table, time_series_plot 

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
geospatial_vars = ["evi_gee", "ndbi_gee", "ndvi_gee", "precip", "temp_air", "temp_ls"]

geospatial_data = {
    geo : load_delta_table(
        geo,
        config, 
        storage_options
    )
    for geo in geospatial_vars
}

## Funciones especificas a cada variable
def render_evi_gee():
    time_series_plot(geospatial_data["evi_gee"], "evi_gee", metadata["evi_gee"], config, storage_options)

def render_ndbi_gee():
    time_series_plot(geospatial_data["ndbi_gee"], "ndbi_gee", metadata["ndbi_gee"], config, storage_options)

def render_ndvi_gee():
    time_series_plot(geospatial_data["ndvi_gee"], "ndvi_gee", metadata["ndvi_gee"], config, storage_options)

def render_precip():
    time_series_plot(geospatial_data["precip"], "precip", metadata["precip"], config, storage_options)

def render_temp_air():
    time_series_plot(geospatial_data["temp_air"], "temp_air", metadata["temp_air"], config, storage_options)
    
def render_temp_ls():
    time_series_plot(geospatial_data["temp_ls"], "temp_ls", metadata["temp_ls"], config, storage_options)
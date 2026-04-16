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

## Funciones especificas a cada variable
def render_evi_gee():
    time_series_plot("evi_gee", metadata["evi_gee"], config, storage_options)

def render_ndbi_gee():
    time_series_plot("ndbi_gee", metadata["ndbi_gee"], config, storage_options)

def render_ndvi_gee():
    time_series_plot("ndvi_gee", metadata["ndvi_gee"], config, storage_options)

def render_precip():
    time_series_plot("precip", metadata["precip"], config, storage_options)

def render_temp_air():
    time_series_plot("temp_air", metadata["temp_air"], config, storage_options)
    
def render_temp_ls():
    time_series_plot("temp_ls", metadata["temp_ls"], config, storage_options)
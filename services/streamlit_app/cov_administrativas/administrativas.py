import tomllib
from pathlib import Path
import polars as pl 

from utils import time_series_plot 

## Carga configuración
FP = Path(".")

## Carga configuración general
with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

## Carga Metadatos de Variables geoespaciales
with open(FP/"metadata"/"admin"/"metadata_admin.toml", "rb") as f:
    metadata = tomllib.load(f)

## Funciones especificas a cada variable
def render_gdp_us_const_trim():
    time_series_plot("gdp_us_const_trim", metadata["gdp_us_const_trim"], config, storage_options)

def render_indice_vol_encad():
    time_series_plot("indice_vol_encad", metadata["indice_vol_encad"], config, storage_options)

def render_remesas_usd_trim():
    time_series_plot("remesas_usd_trim", metadata["remesas_usd_trim"], config, storage_options)

def render_consumo_elect_total():
    time_series_plot("consumo_elect_total", metadata["consumo_elect_total"], config, storage_options)

def render_export_usd_fob():
    time_series_plot("export_usd_fob", metadata["export_usd_fob"], config, storage_options)
    
def render_import_usd_cif():
    time_series_plot("import_usd_cif", metadata["import_usd_cif"], config, storage_options)
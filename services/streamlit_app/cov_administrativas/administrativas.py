import tomllib
from pathlib import Path
import polars as pl 

from utils import time_series_plot 

## Cargamos métodos que construyen las configuraciones generales y del storage
from utils import build_general_config, build_storage_config

## Carga configuración
FP = Path(".")

## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()

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

def render_consumo_elect_al_publico():
    time_series_plot("consumo_elect_al_publico", metadata["consumo_elect_al_publico"], config, storage_options)

def render_consumo_elect_comercio():
    time_series_plot("consumo_elect_comercio", metadata["consumo_elect_comercio"], config, storage_options)

def render_consumo_elect_especiales():
    time_series_plot("consumo_elect_especiales", metadata["consumo_elect_especiales"], config, storage_options)

def render_consumo_elect_industria():
    time_series_plot("consumo_elect_industria", metadata["consumo_elect_industria"], config, storage_options)

def render_consumo_elect_residencial():
    time_series_plot("consumo_elect_residencial", metadata["consumo_elect_residencial"], config, storage_options)

def render_export_usd_fob():
    time_series_plot("export_usd_fob", metadata["export_usd_fob"], config, storage_options)
    
def render_import_usd_cif():
    time_series_plot("import_usd_cif", metadata["import_usd_cif"], config, storage_options)
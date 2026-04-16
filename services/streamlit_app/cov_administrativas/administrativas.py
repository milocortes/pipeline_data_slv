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
with open(FP/"metadata"/"admin"/"metadata_admin.toml", "rb") as f:
    metadata = tomllib.load(f)

## Cargamos tablas 
administrativas_vars = ["gdp_us_const_trim", "indice_vol_encad", "remesas_usd_trim", "consumo_elect_total", "export_usd_fob", "import_usd_cif"]

administrativas_data = {
    geo : load_delta_table(
        geo,
        config, 
        storage_options
    )
    for geo in administrativas_vars
}

## Funciones especificas a cada variable
def render_gdp_us_const_trim():
    time_series_plot(administrativas_data["gdp_us_const_trim"], "gdp_us_const_trim", metadata["gdp_us_const_trim"], config, storage_options)

def render_indice_vol_encad():
    time_series_plot(administrativas_data["indice_vol_encad"], "indice_vol_encad", metadata["indice_vol_encad"], config, storage_options)

def render_remesas_usd_trim():
    time_series_plot(administrativas_data["remesas_usd_trim"], "remesas_usd_trim", metadata["remesas_usd_trim"], config, storage_options)

def render_consumo_elect_total():
    time_series_plot(administrativas_data["consumo_elect_total"], "consumo_elect_total", metadata["consumo_elect_total"], config, storage_options)

def render_export_usd_fob():
    time_series_plot(administrativas_data["export_usd_fob"], "export_usd_fob", metadata["export_usd_fob"], config, storage_options)
    
def render_import_usd_cif():
    time_series_plot(administrativas_data["import_usd_cif"], "import_usd_cif", metadata["import_usd_cif"], config, storage_options)
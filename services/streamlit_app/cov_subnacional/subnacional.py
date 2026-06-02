import tomllib
from pathlib import Path
import polars as pl 

from utils import time_series_plot, time_series_plot_subnacional

## Cargamos métodos que construyen las configuraciones generales y del storage
from utils import build_general_config, build_storage_config

## Carga configuración
FP = Path(".")

## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()

## Carga Metadatos de Variables geoespaciales
with open(FP/"metadata"/"subnacional"/"metadata_subnacional.toml", "rb") as f:
    metadata = tomllib.load(f)

## Funciones especificas a cada variable
def render_gdp_ppp_departamento():
    time_series_plot_subnacional("gdp_ppp_departamento", metadata["gdp_ppp_departamento"], config, storage_options)

def render_electricidad_departamento():
    time_series_plot_subnacional("electricidad_departamento", metadata["electricidad_departamento"], config, storage_options)

def render_viirs_bm_sum_departamento():
    time_series_plot_subnacional("viirs_bm_sum_departamento", metadata["viirs_bm_sum_departamento"], config, storage_options)

def render_poblacion_departamento():
    time_series_plot_subnacional("poblacion_departamento", metadata["poblacion_departamento"], config, storage_options)

def render_gdp_us_corriente():
    time_series_plot("gdp_us_corriente", metadata["gdp_us_corriente"], config, storage_options)





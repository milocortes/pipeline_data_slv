from fredapi import Fred
import tomllib
from pathlib import Path
import polars as pl 
import sys
import os 

## Cargamos métodos que construyen las configuraciones generales y del storage
from utils import build_general_config, build_storage_config

## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()

## Carga token de FRED
api = os.getenv("FRED")

## Obtenemos datos de la serie GDPC1
fred = Fred(api_key=api)
data = fred.get_series('GDPC1')

## Agregamos nombre a la serie
data.name = "gdp_us_const_trim"

## Convertimos Serie a DataFrame
data = data.loc[config["start_date"]:]
data = data.to_frame().reset_index(names = "datetime") 

## Convertimos pd.DataFrame a pl.DataFrame
data = pl.from_pandas(data)

### Guardamos datos en formato Delta Table en RustFS
table_name = sys.argv[0].split(".")[0]

data.write_delta(
    f"s3://{config['BUCKET_NAME']}/gdp_us_const_trim",
    storage_options=storage_options,
    mode = "overwrite"
)



from fredapi import Fred
import tomllib
from pathlib import Path
import polars as pl 
import sys

## Carga configuración
FP = Path(".")

with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga API Key
with open(FP/"config"/"api_keys"/"api_keys.toml", "rb") as f:
    api = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

## Obtenemos datos de la serie GDPC1
fred = Fred(api_key=api["keys"]["fred"])
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



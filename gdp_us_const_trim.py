from fredapi import Fred
import tomllib
from pathlib import Path
import polars as pl 

## Carga configuración
FP = Path(".")

with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga API Key
with open(FP/"config"/"api_keys"/"api_keys.toml", "rb") as f:
    api = tomllib.load(f)

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

### Guardamos datos en formato Delta Table
DL_FP = FP/config["delta_lake_fp"] / "gdp_us_const_trim"
data.write_delta(DL_FP)
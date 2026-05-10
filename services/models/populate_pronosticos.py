import tomllib
from pathlib import Path
import polars as pl

## Carga configuración
FP = Path(".")

## Carga configuración general
with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

### Tabla que guarda los pronósticos del nivel del IVE
columnas_nivel = ["Date", "media_prediccion_nivel"]
datos_nivel = [
    ["2025-04-01", 129.20], 
    ["2025-07-01", 132.24],
    ["2025-10-01", 132.93]
]

nivel_ive = pl.DataFrame(
    datos_nivel, schema = columnas_nivel,  orient="row", strict=False
).with_columns(
    pl.col("Date").str.to_datetime("%Y-%m-%d")
)

## Guardamos datos en formato Delta Table en RustFS
nivel_ive.write_delta(
    f"s3://{config['BUCKET_NAME']}/arimax_pronostico_nivel",
    storage_options=storage_options,
    mode = "overwrite"
)

## Tabla que guarda los pronósticos de la tasa de crecimiento interanual del IVE
columnas_tc_interanual = ["Date", "media_prediccion_tc_interanual"]
datos_tc_interanual = [
    ["2025-04-01", 0.023], 
    ["2025-07-01", 0.049],
    ["2025-10-01", 0.032]
]

tc_interanual = pl.DataFrame(
    datos_tc_interanual, schema = columnas_tc_interanual,  orient="row", strict=False
).with_columns(
    pl.col("Date").str.to_datetime("%Y-%m-%d")
)

## Guardamos datos en formato Delta Table en RustFS
tc_interanual.write_delta(
    f"s3://{config['BUCKET_NAME']}/arimax_pronostico_tc_interanual",
    storage_options=storage_options,
    mode = "overwrite"
)

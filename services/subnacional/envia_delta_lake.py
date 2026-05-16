## Carga paquetes
import tomllib
from pathlib import Path
import polars as pl

## Carga configuración
FP = Path(".")

with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

## Carga salidas del modelo BPVAR
datos = pl.read_csv(
            "pronostico_subnacional_departamentos.csv"
        ).with_columns(
            pl.col("datetime").str.to_datetime("%Y-%m-%d")
        )

### Guardamos datos en formato Delta Table en RustFS
datos.write_delta(
    f"s3://{config['BUCKET_NAME']}/pronostico_subnacional_departamentos",
    storage_options=storage_options,
    mode = "overwrite"
)

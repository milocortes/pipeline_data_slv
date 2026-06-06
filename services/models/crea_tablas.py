import polars as pl
import glob 

## Cargamos métodos que construyen las configuraciones generales y del storage
from utils import build_general_config, build_storage_config

## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()

## Carga tablas
tablas = glob.glob("datos/*.parquet")

## Carga y guarda las tablas en RustFS
for tabla in tablas:
    pl.read_parquet(
        tabla
    ).write_delta(
        f"s3://{config['BUCKET_NAME']}/{tabla.split('/')[-1].split('.')[0]}",
        storage_options=storage_options,
        mode = "overwrite"
    )

import pandas as pd
from blackmarble.extract import bm_extract
from blackmarble.raster import bm_raster
import geopandas as gpd 
import tomllib
from pathlib import Path
import polars as pl
import numpy as np 

## Cargamos métodos que construyen las configuraciones generales y del storage
from utils import build_general_config, build_storage_config

## Carga configuración
FP = Path(".")

## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()

# Set NASA EarthData Token (envvar or alternative recommended)
bearer = os.getenv("BLACKMARBLE")

# Retrieve GADM polygon of Lebanon
gdf = gpd.read_file(
    FP / "geojson" / "gadm41_SLV_1.geojson"
)

# Create NTL dataset from 2012Q1 to today
ntl_df_year_sum = bm_extract(
    gdf,
    product_id= "VNP46A3", #"VNP46A4",
    date_range=pd.date_range("2012-01-01", pd.to_datetime('today'), freq="QE"),
    token=bearer,
    aggfunc = ["sum"],
    variable = "AllAngle_Composite_Snow_Free",
    drop_values_by_quality_flag = (255, 2),        # Valores de mala calidad a filtrar
)

# Columnas minimas
viirs_bm_departamentos = ntl_df_year_sum[["date", "GID_1", "ntl_sum"]]

## Ajusta al inicio del trimestre
viirs_bm_departamentos["date"] = viirs_bm_departamentos["date"] - pd.offsets.QuarterEnd() + pd.offsets.Day()
viirs_bm_departamentos["GID_1"] = viirs_bm_departamentos["GID_1"].str.replace(".","_").str[:-2]

viirs_bm_departamentos = pl.from_pandas(
    viirs_bm_departamentos
        ).with_columns(
            pl.col("ntl_sum").log(), 
            pl.col("date").dt.cast_time_unit("us")
        ).rename(
            {"ntl_sum" : "viirs_bm_sum_departamento"}
)

### Renombramos date to datetime
viirs_bm_departamentos = viirs_bm_departamentos.rename({"date" : "datetime"})

### Guardamos datos en formato Delta Table en RustFS
viirs_bm_departamentos.write_delta(
    f"s3://{config['BUCKET_NAME']}/viirs_bm_departamentos",
    storage_options=storage_options,
    mode = "overwrite"
)

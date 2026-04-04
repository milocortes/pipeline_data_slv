import pandas as pd
from blackmarble.extract import bm_extract
from blackmarble.raster import bm_raster
import geopandas as gpd 
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

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

# Set NASA EarthData Token (envvar or alternative recommended)
bearer = api["keys"]["blackmarble"]

# Retrieve GADM polygon of Lebanon
gdf = gpd.read_file(
    FP / "geojson" / "gadm41_SLV_0.geojson"
)

# Retrive Black Marble Data
bm_data = bm_extract(
    gdf, # this specifies the region of interest
    product_id= "VNP46A3", # this specifies the monthly luminosity data
    #date_range=pd.date_range(config["start_date"], pd.to_datetime('today'), freq="ME"), # this specifies the months
    date_range=pd.date_range("2024-01-01", pd.to_datetime('today'), freq="ME"), # this specifies the months
    token=bearer, # this is the API bearer for NASA LAADS DAAC from Step 3
    aggfunc = ["sum"],
    variable = "AllAngle_Composite_Snow_Free", # this selects the layer we're interested in ->
    drop_values_by_quality_flag = (255, 2), # this drops bad quality observations and coverts them to NA values)
)

## Convertimos el DataFrame a Polars
bm_data = pl.from_pandas(
    bm_data[["date", "ntl_sum"]]
) 


### Agregamos los datos a trimestre
bm_data = bm_data.group_by_dynamic(
    "date", every="1q", closed="left"
    ).agg(
        pl.mean("ntl_sum").alias("viirs_bm_mean"), 
        pl.sum("ntl_sum").alias("viirs_bm_sum"), 
    )

### Renombramos date to datetime
bm_data = bm_data.rename({"date" : "datetime"})

### Guardamos datos en formato Delta Table en RustFS
bm_data.select("datetime", "viirs_bm_mean").write_delta(
    f"s3://{config['BUCKET_NAME']}/viirs_bm_mean",
    storage_options=storage_options,
    mode = "overwrite"
)

bm_data.select("datetime", "viirs_bm_sum").write_delta(
    f"s3://{config['BUCKET_NAME']}/viirs_bm_sum",
    storage_options=storage_options,
    mode = "overwrite"
)

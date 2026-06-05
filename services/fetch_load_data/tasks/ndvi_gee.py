## Paquetería de GEE
import ee

## Carga paquetes
import pandas as pd
from datetime import datetime
import geopandas as gpd 
import json
import tomllib
from pathlib import Path
import polars as pl

## Carga funciones
from gee.gee_functions import (calculateMonthlyNDVI, calculateMonthlyPrecipitation, calculateMonthlyNDBI, 
                              calculateMonthlyTemperature, calculateQuarterlyAggregates, calculateMonthlyEVI, 
                              calculateMonthlyLST)

## Carga configuración
FP = Path(".")

## Cargamos métodos que construyen las configuraciones generales y del storage
from utils import build_general_config, build_storage_config

## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()

## Carga GEE API Key
GEE_API_KEY_FILE_NAME = os.getenv("GEE_API_KEY_FILE")
gee_api_key = str(FP/"config"/"api_keys"/GEE_API_KEY_FILE_NAME)

## Trigger the authentication flow.
service_account = config["service_account_gee"]
credentials = ee.ServiceAccountCredentials(service_account, gee_api_key)

## Initialize the library.
ee.Initialize(project=config["gee_project"], credentials = credentials)

## Subset the El Salvador feature from countries.
## Load country features from Large Scale International Boundary (LSIB) dataset.
countries = ee.FeatureCollection(config["LSIB"])
el_salvador = countries.filter(ee.Filter.eq('ADM0_NAME', 'El Salvador'))
slv = el_salvador.geometry()

## Definimos fechas de inicio y fin de consulta de datos
startDate = ee.Date(config["start_date"])
endDate = ee.Date(pd.to_datetime('today'))

## --------------- NDVI (GEE)
dateRangeMillis_ndvi_gee = ee.List.sequence(startDate.millis(), endDate.millis(), 2.628e+9)

## --------------------------------------
##### Definimos colección de Imágenes
## --------------------------------------
## Colección de imágenes MODIS MOD13Q1 (NDVI mensual, resolución de 250m).
modisCollection = ee.ImageCollection("MODIS/061/MOD13Q1").filterBounds(slv).filterDate(startDate, endDate)

## --------------- NDVI (GEE)
acumula = []

for i in dateRangeMillis_ndvi_gee.getInfo():
    acumula.append(calculateMonthlyNDVI(i, modisCollection, slv))
    print(acumula[-1])

## Creamos DataFrame
ndvi_gee = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)

## Eliminamos datos que aún no han sido registrados por el rezago de actualización
ndvi_gee = ndvi_gee.query("ndvi_value!=-9999")

## Convertimos el DataFrame a Polars
ndvi_gee = pl.from_pandas(ndvi_gee)

### Agregamos los datos a trimestre
ndvi_gee = ndvi_gee.group_by_dynamic("datetime", every="1q", closed="left").agg(pl.mean("ndvi_value"))

### Renombramos nombre
ndvi_gee = ndvi_gee.rename({"ndvi_value" : "ndvi_gee"})

### Guardamos datos en formato Delta Table en RustFS
ndvi_gee.write_delta(
    f"s3://{config['BUCKET_NAME']}/ndvi_gee",
    storage_options=storage_options,
    mode = "overwrite"
)

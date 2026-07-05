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
import os 

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

## ---------------- Pluviosidad (GEE) 
dateRangeMillis_rainfall = ee.List.sequence(startDate.millis(), endDate.millis(), 2.628e+9)

## --------------------------------------
##### Definimos colección de Imágenes
## --------------------------------------
## Colección de imágenes CHIRPS (precipitación mensual).
chirpsCollection = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD').filterBounds(slv).filterDate(startDate, endDate)

## ---------------- Pluviosidad (GEE) 
acumula = []

for i in dateRangeMillis_rainfall.getInfo():

    acumula.append(calculateMonthlyPrecipitation(i, chirpsCollection, slv))
    print(acumula[-1])

## Creamos DataFrame
precip = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)

## Eliminamos datos que aún no han sido registrados por el rezago de actualización
precip = precip.query("precipitation!=-9999")

## Convertimos el DataFrame a Polars
precip = pl.from_pandas(precip)

### Agregamos los datos a trimestre
precip = precip.group_by_dynamic("datetime", every="1q", closed="left").agg(pl.mean("precipitation"))

### Renombramos nombre
precip = precip.rename({"precipitation" : "precip"})

### Guardamos datos en formato Delta Table en RustFS
precip.write_delta(
    f"s3://{config['BUCKET_NAME']}/precip",
    storage_options=storage_options,
    mode = "overwrite"
)

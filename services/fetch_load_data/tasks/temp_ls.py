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

## --------------------------------------
## ---------------- Temperatura Superficie MODIS (GEE) 
## --------------------------------------
dateRangeMillis_temp_sup_gee = ee.List.sequence(startDate.millis(), endDate.millis(), 2.628e+9)


## --------------------------------------
## ----- Definimos colección de Imágenes
## --------------------------------------
## Colección de imágenes MODIS LST.
lstCollection = ee.ImageCollection(
                        'MODIS/061/MOD11A1'
                ).filterBounds(
                    slv
                ).filterDate(
                    startDate, endDate
                )


## ---------------- Temperatura Superficie MODIS (GEE) 
acumula = []

for i in dateRangeMillis_temp_sup_gee.getInfo():
    acumula.append(calculateMonthlyLST(i, lstCollection, slv))
    print(acumula[-1])

## Creamos DataFrame
temp_ls = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)

## Eliminamos datos que aún no han sido registrados por el rezago de actualización
temp_ls = temp_ls.query("LST_Day_1km!=-9999")

## Convertimos el DataFrame a Polars
temp_ls = pl.from_pandas(temp_ls)

### Agregamos los datos a trimestre
temp_ls = temp_ls.group_by_dynamic("datetime", every="1q", closed="left").agg(pl.mean("LST_Day_1km"))

### Renombramos nombre
temp_ls = temp_ls.rename({"LST_Day_1km" : "temp_ls"})

### Guardamos datos en formato Delta Table en RustFS
temp_ls.write_delta(
    f"s3://{config['BUCKET_NAME']}/temp_ls",
    storage_options=storage_options,
    mode = "overwrite"
)
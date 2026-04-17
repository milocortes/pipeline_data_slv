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

with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

## Carga GEE API Key
gee_api_key = str(FP/"config"/"api_keys"/"pib-geoespacial-3ba5fc82e62c.json")


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

## ---------------- EVI (GEE)
dateRangeMillis_ndvi_gee = ee.List.sequence(startDate.millis(), endDate.millis(), 2.628e+9)

## --------------------------------------
##### Definimos colección de Imágenes
## --------------------------------------
## Colección de imágenes MODIS MOD13Q1 (EVI mensual, resolución espacial de 250m)
modisCollectionEVI = ee.ImageCollection(
                            "MODIS/061/MOD13Q1"
                        ).filterBounds(
                            slv
                        ).filterDate(
                            startDate, endDate
                        ).select('EVI') ## Selecciona la banda de EVI

## ---------------- EVI (GEE)
dateRange = ee.List.sequence(0, endDate.difference(startDate, 'month').round().subtract(1))

listOfDates = dateRange.map( lambda n : startDate.advance(n, 'month') )

acumula = []

for i in listOfDates.getInfo():
    acumula.append(calculateMonthlyEVI(i, modisCollectionEVI, slv))
    print(acumula[-1])

## Eliminamos None
acumula = [x for x in acumula if x is not None]

## Creamos DataFrame
evi_gee = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)

## Eliminamos datos que aún no han sido registrados por el rezago de actualización
evi_gee = evi_gee.query("evi_value!=-9999")

## Convertimos el DataFrame a Polars
evi_gee = pl.from_pandas(evi_gee)

### Agregamos los datos a trimestre
evi_gee = evi_gee.group_by_dynamic("datetime", every="1q", closed="left").agg(pl.mean("evi_value"))

### Renombramos nombre
evi_gee = evi_gee.rename({"evi_value" : "evi_gee"})

### Guardamos datos en formato Delta Table en RustFS
evi_gee.write_delta(
    f"s3://{config['BUCKET_NAME']}/evi_gee",
    storage_options=storage_options,
    mode = "overwrite"
)

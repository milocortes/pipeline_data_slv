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

## Trigger the authentication flow.
ee.Authenticate()

## Initialize the library.
ee.Initialize(project="pib-geoespacial")

## Carga funciones
from gee.gee_functions import (calculateMonthlyNDVI, calculateMonthlyPrecipitation, calculateMonthlyNDBI, 
                              calculateMonthlyTemperature, calculateQuarterlyAggregates, calculateMonthlyEVI, 
                              calculateMonthlyLST)

## Carga configuración
FP = Path(".")

with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

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

## Creamos DataFrame
evi_gee = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula[1:]], ignore_index = True)

## Eliminamos datos que aún no han sido registrados por el rezago de actualización
evi_gee = evi_gee.query("evi_value!=-9999")

## Convertimos el DataFrame a Polars
evi_gee = pl.from_pandas(evi_gee)

### Agregamos los datos a trimestre
evi_gee = evi_gee.group_by_dynamic("datetime", every="1q", closed="left").agg(pl.mean("evi_value"))

### Renombramos nombre
evi_gee = evi_gee.rename({"evi_value" : "evi_gee"})

### Guardamos datos en formato Delta Table
DL_FP = FP/config["delta_lake_fp"] / "evi_gee"
evi_gee.write_delta(DL_FP)
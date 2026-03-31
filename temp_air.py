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

## --------------------------------------
## ---------------- Temperatura Aire ERA5 (GEE)
## --------------------------------------

dateRangeMillis_temp_air_gee = ee.List.sequence(startDate.millis(), endDate.millis(), 2.628e+9)

## --------------------------------------
## ----- Definimos colección de Imágenes
## --------------------------------------
## Colección de imágenes ERA5-Land (temperatura del aire mensual).

temperatureCollection = ee.ImageCollection(
                        'ECMWF/ERA5_LAND/MONTHLY_AGGR'
                    ).filterBounds(
                        slv
                    ).filterDate(
                        startDate, endDate
                    )

## ---------------- Temperatura Aire ERA5 (GEE)
acumula = []

for i in dateRangeMillis_temp_air_gee.getInfo():
    acumula.append(calculateMonthlyTemperature(i, temperatureCollection, slv))
    print(acumula[-1])

## Creamos DataFrame
temp_air = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)

## Eliminamos datos que aún no han sido registrados por el rezago de actualización
temp_air = temp_air.query("temperature_2m_celsius!=-9999")

## Convertimos el DataFrame a Polars
temp_air = pl.from_pandas(temp_air)

### Agregamos los datos a trimestre
temp_air = temp_air.group_by_dynamic("datetime", every="1q", closed="left").agg(pl.mean("temperature_2m_celsius"))

### Renombramos nombre
temp_air = temp_air.rename({"temperature_2m_celsius" : "temp_air"})

### Guardamos datos en formato Delta Table
DL_FP = FP/config["delta_lake_fp"] / "temp_air"
temp_air.write_delta(DL_FP)
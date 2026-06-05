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

## ---------------- NDBI (GEE) 
dateRangeMillis_ndbi_gee = ee.List.sequence(startDate.millis(), endDate.millis(), 2.628e+9)

## Cargar la colección MODIS de reflectancia de superficie
modis_ndbi = ee.ImageCollection(
            'MODIS/061/MOD09A1'
        ).filterBounds(
            slv
        ).filterDate(
            startDate, endDate
        )

## Función para calcular el NDBI con el factor de escala
def calculateNDBI(image):
  nir = image.select('sur_refl_b02').multiply(0.0001) # Banda 2: NIR con escala
  swir = image.select('sur_refl_b06').multiply(0.0001) # Banda 6: SWIR con escala
  ndbi = swir.subtract(nir).divide(swir.add(nir)).rename('NDBI')
  return image.addBands(ndbi)

# Aplicar la función a la colección
modisNDBI = modis_ndbi.map(lambda x : calculateNDBI(x))

## ---------------- NDBI (GEE) 
dateRange = ee.List.sequence(0, endDate.difference(startDate, 'month').round().subtract(1))

listOfDates = dateRange.map( lambda n : startDate.advance(n, 'month') )

acumula = []

for i in listOfDates.getInfo():
    acumula.append(calculateMonthlyNDBI(i, modisNDBI, slv))
    print(acumula[-1])

## Creamos DataFrame
ndbi_gee = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)

## Eliminamos datos que aún no han sido registrados por el rezago de actualización
ndbi_gee = ndbi_gee.query("ndbi_value!=-9999")

## Convertimos el DataFrame a Polars
ndbi_gee = pl.from_pandas(ndbi_gee)

### Agregamos los datos a trimestre
ndbi_gee = ndbi_gee.group_by_dynamic("datetime", every="1q", closed="left").agg(pl.mean("ndbi_value"))

### Renombramos nombre
ndbi_gee = ndbi_gee.rename({"ndbi_value" : "ndbi_gee"})

### Guardamos datos en formato Delta Table en RustFS
ndbi_gee.write_delta(
    f"s3://{config['BUCKET_NAME']}/ndbi_gee",
    storage_options=storage_options,
    mode = "overwrite"
)

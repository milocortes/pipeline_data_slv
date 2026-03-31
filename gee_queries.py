## Paquetería de GEE
import ee

## Carga paquetes
import pandas as pd
from datetime import datetime
import geopandas as gpd 
import json

## Trigger the authentication flow.
ee.Authenticate()

## Initialize the library.
ee.Initialize(project="pib-geoespacial")

## Carga funciones
from gee.gee_functions import (calculateMonthlyNDVI, calculateMonthlyPrecipitation, calculateMonthlyNDBI, 
                              calculateMonthlyTemperature, calculateQuarterlyAggregates, calculateMonthlyEVI, 
                              calculateMonthlyLST)

## Subset the El Salvador feature from countries.
## Load country features from Large Scale International Boundary (LSIB) dataset.
countries = ee.FeatureCollection('FAO/GAUL/2015/level0')
el_salvador = countries.filter(ee.Filter.eq('ADM0_NAME', 'El Salvador'))
slv = el_salvador.geometry()

## Import data
today = ee.Date(pd.to_datetime('today'))

## Generar una lista de fechas como milisegundos para cada coleccion de imágenes

## ---------------- Pluviosidad (GEE) 
startDate = ee.Date('1981-01-01')
endDate = ee.Date(pd.to_datetime('today'))

dateRangeMillis_rainfall = ee.List.sequence(startDate.millis(), endDate.millis(), 2.628e+9)

## --------------- NDVI (GEE)
startDate = ee.Date('2000-01-01')
dateRangeMillis_ndvi_gee = ee.List.sequence(startDate.millis(), endDate.millis(), 2.628e+9)

## ---------------- Temperatura Aire ERA5 (GEE)
startDate = ee.Date('1990-01-01')
dateRangeMillis_temp_air_gee = ee.List.sequence(startDate.millis(), endDate.millis(), 2.628e+9)

## ---------------- Temperatura Superficie MODIS (GEE) 
startDate = ee.Date('2000-01-01')
dateRangeMillis_temp_sup_gee = ee.List.sequence(startDate.millis(), endDate.millis(), 2.628e+9)

## --------------------------------------
##### Definimos colección de Imágenes
## --------------------------------------

## ----------------- Luces VIIRS Colorado School of Mines (GEE)
## Colección de imágenes de luces nocturnas VIIRS
viirsCollection = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG').select('avg_rad') #Seleccionar la banda de radiancia promedio

## ---------------- Pluviosidad (GEE) 
## Colección de imágenes CHIRPS (precipitación mensual).
chirpsCollection = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD').filterBounds(slv).filterDate('1981-01-01', today)

## --------------- NDVI (GEE)
## Colección de imágenes MODIS MOD13Q1 (NDVI mensual, resolución de 250m).
modisCollection = ee.ImageCollection("MODIS/061/MOD13Q1").filterBounds(slv).filterDate('2000-01-01', today)

## ---------------- EVI (GEE)
## Colección de imágenes MODIS MOD13Q1 (EVI mensual, resolución espacial de 250m)
modisCollectionEVI = ee.ImageCollection(
                            "MODIS/061/MOD13Q1"
                        ).filterBounds(
                            slv
                        ).filterDate(
                            '2000-01-01', today
                        ).select('EVI') ## Selecciona la banda de EVI

## ---------------- NDBI (GEE) 
## Cargar la colección MODIS de reflectancia de superficie
modis_ndbi = ee.ImageCollection(
            'MODIS/061/MOD09A1'
        ).filterBounds(
            slv
        ).filterDate(
            '2000-02-24', ee.Date(today)
        )

## Función para calcular el NDBI con el factor de escala
def calculateNDBI(image):
  nir = image.select('sur_refl_b02').multiply(0.0001) # Banda 2: NIR con escala
  swir = image.select('sur_refl_b06').multiply(0.0001) # Banda 6: SWIR con escala
  ndbi = swir.subtract(nir).divide(swir.add(nir)).rename('NDBI')
  return image.addBands(ndbi)

# Aplicar la función a la colección
modisNDBI = modis_ndbi.map(lambda x : calculateNDBI(x))

## ---------------- Temperatura Aire ERA5 (GEE)
## Colección de imágenes ERA5-Land (temperatura del aire mensual).
temperatureCollection = ee.ImageCollection(
                        'ECMWF/ERA5_LAND/MONTHLY_AGGR'
                    ).filterBounds(
                        slv
                    ).filterDate(
                        '1990-01-01', today
                    )

## ---------------- Temperatura Superficie MODIS (GEE) 
## Colección de imágenes MODIS LST.
lstCollection = ee.ImageCollection(
                        'MODIS/061/MOD11A1'
                ).filterBounds(
                    slv
                ).filterDate(
                    '2000-01-01', today
                )


"""
 GET VALUES
"""



## ----------------- Luces VIIRS Colorado School of Mines (GEE)
slv_shp = gpd.read_file("data/gadm41_SLV_0/gadm41_SLV_0.shp")
slv_json = slv_shp.to_json()

slv_fc = ee.FeatureCollection(
    json.loads(slv_json)
    ).geometry()

## Generar lista de años y trimestres disponibles en VIIRS (2012 - presente)
years = ee.List.sequence(2012, ee.Date(pd.to_datetime('today')).get('year'))
trimesters = ee.List.sequence(1, 4)

acumula = []

for year in years.getInfo():
    for trimester in trimesters.getInfo():
        acumula.append(
            calculateQuarterlyAggregates(year, trimester, viirsCollection, slv_fc)
        )
        print(acumula[-1])

viirs_csm = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)
viirs_csm.to_csv("ana/data/raw/VIIRS/VIIRS_ElSalvador_Quarterly_Aggregates-GEE-modif.csv", index = False)


## ---------------- Pluviosidad (GEE) 
acumula = []

for i in dateRangeMillis_rainfall.getInfo():

    acumula.append(calculateMonthlyPrecipitation(i, chirpsCollection, slv))
    print(acumula[-1])

precip = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)
precip.to_csv("ana/data/raw/Pluviosidad/Precipitation_ElSalvador_Monthly_CHIRPS.csv", index = False)


## --------------- NDVI (GEE)
acumula = []

for i in dateRangeMillis_ndvi_gee.getInfo():
    acumula.append(calculateMonthlyNDVI(i, modisCollection, slv))
    print(acumula[-1])

ndvi_gee = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)
ndvi_gee.to_csv("ana/data/raw/Vegetacion/NDVI_ElSalvador_Monthly_MOD13Q1.csv", index = False)


## ---------------- EVI (GEE)

startDate = ee.Date('2000-01-01')
endDate = ee.Date(today)
dateRange = ee.List.sequence(0, endDate.difference(startDate, 'month').round().subtract(1))

listOfDates = dateRange.map( lambda n : startDate.advance(n, 'month') )

acumula = []

for i in listOfDates.getInfo():
    acumula.append(calculateMonthlyEVI(i, modisCollection, slv))
    print(acumula[-1])

evi_gee = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula[1:]], ignore_index = True)
evi_gee.to_csv("ana/data/raw/Vegetacion/EVI_ElSalvador_Monthly_MOD13Q1.csv", index = False)


## ---------------- NDBI (GEE) 
startDate = ee.Date('2000-02-24')
endDate = ee.Date(today)
dateRange = ee.List.sequence(0, endDate.difference(startDate, 'month').round().subtract(1))

listOfDates = dateRange.map( lambda n : startDate.advance(n, 'month') )

acumula = []

for i in listOfDates.getInfo():
    acumula.append(calculateMonthlyNDBI(i, modisNDBI, slv))
    print(acumula[-1])

ndbi_gee = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)
ndbi_gee.to_csv("ana/data/raw/Urbanizacion/MODIS_NDBI_ElSalvador_Monthly.csv", index = False)

## ---------------- Temperatura Aire ERA5 (GEE)
acumula = []

for i in dateRangeMillis_temp_air_gee.getInfo():
    acumula.append(calculateMonthlyTemperature(i, temperatureCollection, slv))
    print(acumula[-1])

temp_air = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)
temp_air.to_csv("ana/data/raw/Temperatura/Temperatura_ElSalvador_Monthly_ERA5_Celsius.csv", index = False)

## ---------------- Temperatura Superficie MODIS (GEE) 
acumula = []

for i in dateRangeMillis_temp_sup_gee.getInfo():
    acumula.append(calculateMonthlyLST(i, lstCollection, slv))
    print(acumula[-1])

temp_ls = pd.concat([pd.DataFrame({ k : [v] for k,v in datos.items()}) for datos in acumula], ignore_index = True)
temp_ls.to_csv("ana/data/raw/Temperatura/LST_ElSalvador_Monthly_MODIS.csv", index = False)
import pandas as pd
from datetime import datetime

import ee

## Luces VIIRS Colorado School of Mines (GEE)
def get_viirs_csm(
        month_start : datetime.timestamp,
        month_end : datetime.timestamp,
        slv_geometry : ee.geometry.Geometry
    ) -> pd.DataFrame:

    # Ajusta meses
    month_start_str = str(month_start).split()[0]
    month_end_str = str(month_end).split()[0]

    print(
        f"Month Start : {month_start_str} - Month End : {month_end_str}"
    )
    
    # Filtra dataset al periodo a calcular
    #ee_dataset = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG').filter(ee.Filter.date(month_start_str, month_end_str))
    ee_dataset = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG').filter(ee.Filter.date(month_start_str, month_end_str))
    nighttime = ee_dataset.select('avg_rad').sum()

    # Compute sum VIIRS
    stats = nighttime.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=slv_geometry,
        scale=500, # Resolución de VIIRS ~500m
        maxPixels=1e13
    )

    stats_val = stats.get("avg_rad").getInfo()
    
    # Compute mean VIIRS
    stats_mean = nighttime.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=slv_geometry,
        scale=500, # Resolución de VIIRS ~500m
        maxPixels=1e13
    )

    stats_mean_val = stats_mean.get("avg_rad").getInfo()

    
    return pd.DataFrame(
        {
            "country" : ["El Salvador"],
            "date" : [month_end_str],
            "year" : [month_end.year],
            "month" : [month_end.month],
            "lights_mean" : [stats_mean_val],
            "lights_sum" : [stats_val],  
        }
    )
    
def month_to_quarter(month : int):
    match month:
        case 1 | 2 | 3 :
            return 1
        case 4 | 5 | 6 :
            return 2
        case 7 | 8 | 9 :
            return 3
        case 10 | 11 | 12 :
            return 4        


## ----------------- Luces VIIRS Colorado School of Mines (GEE)

# Función para calcular agregados trimestrales
def calculateQuarterlyAggregates(year, trimester, img_collection, aoi):
    # Definir los meses correspondientes a cada trimestre
    startMonth = ee.Number(trimester).subtract(1).multiply(3).add(1)
    startDate = ee.Date.fromYMD(year, startMonth, 1)
    endDate = startDate.advance(3, 'month')
    
    # Filtrar imágenes en el trimestre y calcular el promedio
    quarterlyImage = img_collection.filterDate(startDate, endDate).sum() # Suma de las imágenes en el trimestre

    # Verificar si la imagen existe para evitar errores nulos
    imageExists = quarterlyImage.bandNames().size().gt(0)
  
    # Calcular estadísticas solo si la imagen existe
    stats = ee.Algorithms.If(imageExists, quarterlyImage.reduceRegion(
        reducer = ee.Reducer.sum(),
        geometry = aoi,
        scale = 500,  # Resolución de VIIRS ~500m
        maxPixels = 1e13
    ), None)
    
    statsMean = ee.Algorithms.If(imageExists, quarterlyImage.reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = aoi,
        scale = 500,
        maxPixels = 1e13
    ), None)

    return {
        'country': 'El Salvador',
        'datetime' : pd.to_datetime(startDate.getInfo()["value"], unit='ms'),
        'year': year,
        'trimester': month_to_quarter(startMonth.getInfo()),
        'lights_sum': ee.Algorithms.If(
                            imageExists, 
                            ee.Dictionary(stats).get('avg_rad'), None
                        ).getInfo(),
        'lights_mean': ee.Algorithms.If(
                            imageExists, 
                            ee.Dictionary(statsMean).get('avg_rad'), None
                        ).getInfo(),
    }


## ---------------- Pluviosidad (GEE) 
## Función para calcular la precipitación mensual total.
def calculateMonthlyPrecipitation(date, img_collection, aoi):
    startDateMonth = ee.Date(date)
    endDateMonth = startDateMonth.advance(1, 'month')
    year = startDateMonth.get('year')
    month = startDateMonth.get('month')

    ## Calculate the number of days in the month
    daysInMonth = endDateMonth.difference(startDateMonth, 'day')

    monthlyImages = img_collection.filterDate(startDateMonth, endDateMonth);
    count = monthlyImages.size()

    precipitationValue = ee.Algorithms.If(
        count.gt(0),
        monthlyImages.sum().multiply(daysInMonth).reduceRegion( ## Sum and multiply by days in month
            reducer = ee.Reducer.mean(),
            geometry = aoi,
            scale = 5000, ## Resolución de CHIRPS: aprox. 5km
            maxPixels =  1e13
        ).get('precipitation'),
        -9999
    )

    return {
        'country': 'El Salvador',
        'datetime' : pd.to_datetime(startDateMonth.getInfo()["value"], unit='ms'),
        'year': year.getInfo(),
        'month': month.getInfo(),
        'precipitation': precipitationValue.getInfo() ## Precipitación en mm
    }
## --------------- NDVI (GEE)
## Función para calcular el NDVI mensual
def calculateMonthlyNDVI(date, 
                         img_collection, 
                         aoi):

    startDateMonth = ee.Date(date)
    endDateMonth = startDateMonth.advance(1, 'month')
    year = startDateMonth.get('year')
    month = startDateMonth.get('month')

    monthlyImages = img_collection.filterDate(startDateMonth, endDateMonth)
    count = monthlyImages.size()

    ndviValue = ee.Algorithms.If(
        count.gt(0),
        monthlyImages.select('NDVI').map(

            lambda image : image.multiply(0.0001)
        ).median().reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = aoi,
            scale = 250,
            maxPixels = 1e13
        ).get('NDVI'),
        -9999
    )

    return {
        'country': 'El Salvador',
        'datetime' : pd.to_datetime(startDateMonth.getInfo()["value"], unit='ms'),
        'year': year.getInfo(),
        'month': month.getInfo(),
        'ndvi_value': ndviValue.getInfo()
    }

## ---------------- EVI (GEE)
## Función para calcular el EVI mensual
def calculateMonthlyEVI(date, 
                         img_collection, 
                         aoi):
                        
    startDateMonth = ee.Date(date["value"])
    endDateMonth = startDateMonth.advance(1, 'month')
    year = startDateMonth.get('year')
    month = startDateMonth.get('month')

    ## Filtrar las imágenes de MOD13Q1 para cada mes
    monthlyImages = img_collection.filterDate(startDateMonth, endDateMonth)


    ## Check if there are any images in the collection for the current month
    imageCount = monthlyImages.size()

    if (imageCount.getInfo() > 0):
      # Crear un mosaico mensual (composición de imágenes)
      monthlyEVI = monthlyImages.median().clip(aoi)

      # Calcular el valor promedio de EVI para la región y transformar a escala (-1 a 1)
      eviDict = monthlyEVI.reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = aoi,
        scale = 250,  # Resolución espacial de MODIS: 250m
        maxPixels = 1e13,
        bestEffort = True
      )

      # Verifica si hay datos de EVI
      eviRaw = eviDict.get('EVI')

      if (eviRaw != None) :  # Solo agregar si hay datos
        eviScaled = ee.Number(eviRaw).divide(10000); # Escalar EVI a (-0.2, 1)

        return {
          'country': 'El Salvador',
          'datetime' : pd.to_datetime(startDateMonth.getInfo()["value"], unit='ms'),
          'year': year.getInfo(),
          'month': month.getInfo(),
          'evi_value': eviScaled.getInfo()
        }

      
    else :
      print('No MODIS data found for EVI for ' + str(year.getInfo()) + '-' + str(month.getInfo()))

## ---------------- NDBI (GEE) 
## Función para calcular el NDBI mensual
def calculateMonthlyNDBI(date, 
                         img_collection, 
                         aoi):
    
    startDateMonth = ee.Date(date["value"])
    endDateMonth = startDateMonth.advance(1, 'month')
    year = startDateMonth.get('year')
    month = startDateMonth.get('month')

    filtered = img_collection.filterDate(startDateMonth, endDateMonth)
    monthlyNDBI = filtered.select('NDBI').mean().clip(aoi)

    ndbiDict = monthlyNDBI.reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = aoi,
        scale = 500,
        maxPixels = 1e13
    )
  
    ndbiValue = ee.Algorithms.If(ndbiDict.contains('NDBI'), ndbiDict.get('NDBI'), -9999)

    return {
        'country': 'El Salvador',
        'datetime' : pd.to_datetime(startDateMonth.getInfo()["value"], unit='ms'),
        'year': year.getInfo(),
        'month': month.getInfo(),
        'ndbi_value': ndbiValue.getInfo()
    }

## ---------------- Temperatura Aire ERA5 (GEE)
## Función para calcular la temperatura mensual promedio en grados Celsius.
def calculateMonthlyTemperature(date, img_collection, aoi):

    startDateMonth = ee.Date(date)
    endDateMonth = startDateMonth.advance(1, 'month')
    year = startDateMonth.get('year')
    month = startDateMonth.get('month')

    monthlyImages = img_collection.filterDate(startDateMonth, endDateMonth)
    count = monthlyImages.size()

    temperatureValueCelsius = ee.Algorithms.If(
        count.gt(0),
        monthlyImages.select('temperature_2m').mean().subtract(273.15).reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = aoi,
            scale = 9000, ## Resolución de ERA5-Land: aprox. 9km
            maxPixels = 1e13
        ).get('temperature_2m'),
        -9999
    )

    return {
        'country': 'El Salvador',
        'datetime' : pd.to_datetime(startDateMonth.getInfo()["value"], unit='ms'),
        'year': year.getInfo(),
        'month': month.getInfo(),
        'temperature_2m_celsius': temperatureValueCelsius.getInfo() ## Temperatura en grados Celsius (°C)
    }

## ---------------- Temperatura Superficie MODIS (GEE) 
## Función para calcular la temperatura LST mensual promedio.
def calculateMonthlyLST(date, img_collection, aoi):
    startDateMonth = ee.Date(date)
    endDateMonth = startDateMonth.advance(1, 'month')
    year = startDateMonth.get('year')
    month = startDateMonth.get('month')

    monthlyImages = img_collection.filterDate(startDateMonth, endDateMonth)
    count = monthlyImages.size()

    lstValue = ee.Algorithms.If(
        count.gt(0),
        monthlyImages.select('LST_Day_1km').mean().multiply(0.02).subtract(273.15).reduceRegion(
            reducer= ee.Reducer.mean(),
            geometry= aoi,
            scale= 1000,
            maxPixels= 1e13
        ).get('LST_Day_1km'),
        -9999
    )

    return {
        'country': 'El Salvador',
        'datetime' : pd.to_datetime(startDateMonth.getInfo()["value"], unit='ms'),
        'year': year.getInfo(),
        'month': month.getInfo(),
        'LST_Day_1km': lstValue.getInfo() ## Temperatura en grados Celsius (°C)
    }


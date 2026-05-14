import tomllib
from pathlib import Path
import polars as pl 

from typing import List, Dict
import numpy as np 

from deltalake import DeltaTable

## Carga configuración
FP = Path(".")

## Carga configuración general
with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

## Carga Metadatos de Variables administrativas
with open(FP/"metadata"/"admin"/"metadata_admin.toml", "rb") as f:
    metadata_admin = tomllib.load(f)

## Carga Metadatos de Variables geoespaciales
with open(FP/"metadata"/"geoespacial"/"metadata_geoespacial.toml", "rb") as f:
    metadata_geoespacial = tomllib.load(f)

## Funcion que prueba si están disponibles las covariables para el pronóstico de los modelos ARIMAX
def available_cov_arimax(
            config : Dict[str,str], 
            storage_config : Dict[str,str], 
            metadata_admin : Dict[str,str], 
            metadata_geoespacial : Dict[str,str], 
            ) -> List[str]: 

    ## Lista de Covariables
    covariables = ['consumo_elect_al_publico', 'consumo_elect_comercio', 'consumo_elect_industria',
    'consumo_elect_total', 'evi_gee', 'ndvi_gee', 'precip', 'remesas_usd_trim', 'temp_ls', 'viirs_bm_sum', 'gdp_us_const_trim']

    ## Variable de respuesta
    respuesta = "indice_vol_encad"

    ## Consolidamos tablas
    ### Primero verificaremos si existen las tablas en Delta Lake.
    ### Si existen, cargamos las tablas. En caso contrario, guardamos la tabla que 
    ### no existe en `no_existen_tablas`

    no_existen_tablas = []
    datos = []

    for cov in covariables + [respuesta]:
        test_table = DeltaTable.is_deltatable(f"s3://{config['BUCKET_NAME']}/{cov}", storage_options)

        if test_table:
            datos.append(
                pl.read_delta(
                    f"s3://{config['BUCKET_NAME']}/{cov}",
                    storage_options=storage_options,
                )
            )
        else:
            no_existen_tablas.append(
                cov
            )

    datos = pl.concat(datos,  how = "align")

    # Filtramos los valores para el trimestre posterior al último valor disponible del IVE
    datos = datos.filter(
        pl.col("datetime") <= pl.col("datetime").filter(
            pl.col(respuesta).is_not_null()
        ).max().dt.offset_by("3mo")
    )   

    # Obtenemos un diccionario con el último valor disponible de las covariables
    covariables_tablas_existentes = list(set(covariables) - set(no_existen_tablas))
    last_q_datos = datos.select(covariables_tablas_existentes).tail(1).to_dicts()[0]

    # Lista con las covariables que no se encuentran disponibles para la fecha de la estimación
    datos_no_disponibles = [i for i,j in last_q_datos.items() if not j]

    # Agregamos las variables para las cuales no existen tablas
    datos_no_disponibles += no_existen_tablas

    # Cambia nomenclatura de variable por su nombre completo
    datos_no_disponibles = [metadata_admin[cov]["variable"] if cov in metadata_admin else cov for cov in datos_no_disponibles ]
    datos_no_disponibles = [metadata_geoespacial[cov]["variable"] if cov in metadata_geoespacial else cov for cov in datos_no_disponibles ]

    return datos_no_disponibles

def get_available_cov_arimax() -> List[str]:
    return available_cov_arimax(
            config,
            storage_options, 
            metadata_admin,
            metadata_geoespacial, 
            ) 
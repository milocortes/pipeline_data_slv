import tomllib
from pathlib import Path
import polars as pl 

from typing import List, Dict
import numpy as np 

from deltalake import DeltaTable

## Cargamos métodos que construyen las configuraciones generales y del storage
from utils import build_general_config, build_storage_config

## Carga configuración
FP = Path(".")

## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()

## Carga Metadatos de Variables administrativas
with open(FP/"metadata"/"admin"/"metadata_admin.toml", "rb") as f:
    metadata_admin = tomllib.load(f)

## Carga Metadatos de Variables geoespaciales
with open(FP/"metadata"/"geoespacial"/"metadata_geoespacial.toml", "rb") as f:
    metadata_geoespacial = tomllib.load(f)

## Carga Metadatos de Variables Subnacionales
with open(FP/"metadata"/"subnacional"/"metadata_subnacional.toml", "rb") as f:
    metadata_subnacional = tomllib.load(f)

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

    # Si todas las columnas (covariables + IVE) tienen valores para el último registro del dataframe
    # Ninguna covariable cuenta con información para el pronóstico del siguiente trimestre del IVE.
    # Nos faltan todas las covariables.
    if all(datos.row(-1)):
        
        # Lista que tiene todas las covariables
        datos_no_disponibles = covariables[:]

        # Cambia nomenclatura de variable por su nombre completo
        datos_no_disponibles = [metadata_admin[cov]["variable"] if cov in metadata_admin else cov for cov in datos_no_disponibles ]
        datos_no_disponibles = [metadata_geoespacial[cov]["variable"] if cov in metadata_geoespacial else cov for cov in datos_no_disponibles ]

        return datos_no_disponibles

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

## Funcion que prueba si están disponibles las covariables para el pronóstico de los modelos ARIMAX
def available_cov_ml(
            config : Dict[str,str], 
            storage_config : Dict[str,str], 
            metadata_admin : Dict[str,str], 
            metadata_geoespacial : Dict[str,str], 
            ) -> List[str]: 

    ## Lista de Covariables
    covariables = [ 'consumo_elect_al_publico', 'consumo_elect_comercio', 'consumo_elect_industria',
                'consumo_elect_total', 'consumo_elect_especiales', 'consumo_elect_residencial', 
                'evi_gee', 'ndbi_gee', 'ndvi_gee', 'precip', 'remesas_usd_trim', 'temp_air', 'temp_ls', 'viirs_bm_sum', 
                'gdp_us_const_trim', 'import_usd_cif', 'export_usd_fob']

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

    # Si todas las columnas (covariables + IVE) tienen valores para el último registro del dataframe
    # Ninguna covariable cuenta con información para el pronóstico del siguiente trimestre del IVE.
    # Nos faltan todas las covariables.
    if all(datos.row(-1)):
        
        # Lista que tiene todas las covariables
        datos_no_disponibles = covariables[:]

        # Cambia nomenclatura de variable por su nombre completo
        datos_no_disponibles = [metadata_admin[cov]["variable"] if cov in metadata_admin else cov for cov in datos_no_disponibles ]
        datos_no_disponibles = [metadata_geoespacial[cov]["variable"] if cov in metadata_geoespacial else cov for cov in datos_no_disponibles ]

        return datos_no_disponibles
        
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

def get_available_cov_ml() -> List[str]:
    return available_cov_ml(
            config,
            storage_options, 
            metadata_admin,
            metadata_geoespacial, 
            ) 


## Funcion que prueba si están disponibles las covariables para el pronóstico del Modelo Subnacional
def available_cov_subnacional(
            config : Dict[str,str], 
            storage_config : Dict[str,str], 
            metadata_admin : Dict[str,str], 
            metadata_geoespacial : Dict[str,str], 
            ) -> List[str]: 

    ## Lista de Covariables
    covariables = [ 'poblacion_departamento', 'viirs_bm_sum_departamento', 'electricidad_departamento']

    ## Variable de respuesta
    respuesta = 'gdp_us_corriente'

    ## Obtenemos la fecha del último valor disponible de PIB Corriente
    pib_corriente = pl.read_delta(
                    f"s3://{config['BUCKET_NAME']}/{respuesta}",
                    storage_options=storage_options,
                )

    date_pib_corriente = pib_corriente.select(pl.col("datetime").last()).item()


    ## Consolidamos tablas
    ### Primero verificaremos si existen las tablas en Delta Lake.
    ### Si existen, cargamos las tablas. En caso contrario, guardamos la tabla que 
    ### no existe en `no_existen_tablas`

    no_existen_tablas = []
    datos_no_disponibles = []
    datos = []

    for cov in covariables + [respuesta]:
        test_table = DeltaTable.is_deltatable(f"s3://{config['BUCKET_NAME']}/{cov}", storage_options)

        if test_table:
            
            data_cov = pl.read_delta(
                    f"s3://{config['BUCKET_NAME']}/{cov}",
                    storage_options=storage_options,
                )

            date_data_cov = data_cov.select(pl.col("datetime").last()).item()

            ## Verifica si la última fecha disponible de la covariable es mayor o igual 
            ## a la fecha del último valor disponible de PIB Corriente. 
            ## Si se cumple la condición, podemos usar la covariable para la estimación
            if date_data_cov >= date_pib_corriente:
                pass
            else:
                # Lista con las covariables que no se encuentran disponibles para la fecha de la estimación
                datos_no_disponibles.append(
                    cov
                )
                    
        else:
            no_existen_tablas.append(
                cov
            )

    # Agregamos las variables para las cuales no existen tablas
    datos_no_disponibles += no_existen_tablas

    # Cambia nomenclatura de variable por su nombre completo
    datos_no_disponibles = [metadata_subnacional[cov]["variable"] if cov in metadata_subnacional else cov for cov in datos_no_disponibles ]

    return datos_no_disponibles

def get_available_cov_subnacional() -> List[str]:
    return available_cov_subnacional(
            config,
            storage_options, 
            metadata_admin,
            metadata_geoespacial, 
            ) 
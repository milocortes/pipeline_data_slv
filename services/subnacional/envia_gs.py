import tomllib
from pathlib import Path
import polars as pl
import pandas as pd
import polars.selectors as cs
import numpy as np 

## GS packages
import gspread
from google.oauth2.service_account import Credentials

## Disable Warnings
import warnings
warnings.filterwarnings("ignore")

## Carga rich
from rich.console import Console
console = Console()

## Cargamos métodos que construyen las configuraciones generales y del storage
from utils import build_general_config, build_storage_config

## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()

# 1. Authenticate
console.print("1.-", "Autenticando en GS", style="bold red")

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('config/api_keys/pronosticos-493700-56f57502ffb3.json', scopes=scopes)
client = gspread.authorize(creds)

# 3. Open Google Sheet and update
sh = client.open("insumos-tablero-pib")

# Diccionario de tabs de Google Sheet
sheets = [
            "subnacional-desagregacion",
            "subnacional-departamentos", 
            "nivel-subnacional-departamentos", 
            "tc-interanual-subnacional-departamentos"
        ]

worksheets = {sheet : sh.worksheet(sheet) for sheet in sheets}

# Cargamos tablas de ponderadores por departamento y del PIB Trimestral a precios corrientes
console.print("2.-", "Construyendo Tablas para GS", style="bold red")

deptos = pl.read_delta(
        f"s3://{config['BUCKET_NAME']}/pronostico_subnacional_departamentos",
        storage_options=storage_options,
    )

pib = pl.read_delta(
        f"s3://{config['BUCKET_NAME']}/gdp_us_corriente",
        storage_options=storage_options,
    )

# Reunimos dataframes para calcular el PIB departamental
deptos = deptos.join(
    pib, 
    on = "datetime", 
    how = "left"
)


## Agrega nombre de departamentos
deptos_name = {'SLV_1': 'Ahuachapán',
 'SLV_2': 'Cabañas',
 'SLV_3': 'Chalatenango',
 'SLV_4': 'Cuscatlán',
 'SLV_5': 'La Libertad',
 'SLV_6': 'La Paz',
 'SLV_7': 'La Unión',
 'SLV_8': 'Morazán',
 'SLV_9': 'San Miguel',
 'SLV_10': 'San Salvador',
 'SLV_11': 'San Vicente',
 'SLV_12': 'Santa Ana',
 'SLV_13': 'Sonsonate',
 'SLV_14': 'Usulután'}

deptos = deptos.with_columns(
    pl.col("gdp_us_corriente")*pl.col("ponderador"),
    pl.col("departamento").replace(deptos_name)
)

## ++++++++++++++++++++++++++++++++++++++++++++++++++++++ ##
##                                                        ##
##        PREPARA TABLAS PARA ENVIARSE A GS               ##
##                                                        ##
## ++++++++++++++++++++++++++++++++++++++++++++++++++++++ ##

####----------------------------------------------- ####
####           subnacional-desagregacion
####----------------------------------------------- ####

last_date = pib.select(pl.col("datetime").max()).item()

subnacional_desagregacion = deptos.filter(
                                datetime = last_date
                            ).drop("datetime").rename(
                                {
                                    "departamento" : "Departamento", 
                                    "ponderador" : "Ponderador", 
                                    "gdp_us_corriente" : "PIB Corriente"
                                }
                            ).with_columns(
                                cs.float().round(3) # Redondeamos a tres digitos
                            )



####----------------------------------------------- ####
####           subnacional-departamentos
####----------------------------------------------- ####

subnacional_departamentos = deptos.select(
                                "datetime", "departamento", "gdp_us_corriente"
                            ).rename(
                                {   
                                    "datetime" : "Date",
                                    "departamento" : "Departamento", 
                                    "gdp_us_corriente" : "PIB Corriente"
                                }
                            ).with_columns(
                                cs.float().round(3) # Redondeamos a tres digitos
                            )

# Construimos serie de crecimiento trimestral y crecimiento interanual
def crecimiento_trimestral(columna : str) -> pl.Expr : 
    return (
            (
                pl.col(columna)/pl.col(columna).shift(1)
            ) - 1  
        ).alias("Crecimiento Trimestral")

def crecimiento_interanual(columna : str) -> pl.Expr : 
    return (
            (
                pl.col(columna)/pl.col(columna).shift(4)
            ) - 1  
        ).alias("Crecimiento Interanual")

subnacional_departamentos = subnacional_departamentos.with_columns(
                    crecimiento_interanual("PIB Corriente"), 
                    crecimiento_trimestral("PIB Corriente"), 
                ).filter(
                    Date = last_date
                ).select(
                    "Date", "Departamento", "Crecimiento Trimestral", "Crecimiento Interanual", "PIB Corriente"
                ).with_columns(
                    cs.float().round(3) # Redondeamos a tres digitos
                )

####----------------------------------------------- ####
####           nivel-subnacional-departamentos
####----------------------------------------------- ####

nivel_subnacional_departamentos = deptos.select(
                                "datetime", "departamento", "gdp_us_corriente"
                            ).rename(
                                {   
                                    "datetime" : "Date",
                                    "departamento" : "Departamento", 
                                    "gdp_us_corriente" : "PIB Corriente"
                                }
                            ).with_columns(
                                cs.float().round(3) # Redondeamos a tres digitos
                            )

####----------------------------------------------- ####
####           tc-interanual-subnacional-departamentos
####----------------------------------------------- ####
subnacional_departamentos_departamentos = deptos.select(
                                "datetime", "departamento", "gdp_us_corriente"
                            ).rename(
                                {   
                                    "datetime" : "Date",
                                    "departamento" : "Departamento", 
                                    #"gdp_us_corriente" : "PIB Corriente"
                                }
                            ).with_columns(
                                crecimiento_interanual("gdp_us_corriente")
                            ).drop("gdp_us_corriente").drop_nulls().with_columns(
                                cs.float().round(3) # Redondeamos a tres digitos
                            )

#### Guardamos dataframes de salida en un diccionario
def ajusta_df(
    datos : pl.DataFrame
    ) -> pd.DataFrame:
    return datos.with_columns(
        pl.col("Date")
            .dt.truncate("1q")
            .dt.offset_by("2mo")
            .dt.month_end().dt.strftime("%Y-%m-%d")
        ).to_pandas().replace(np.nan, "")

### Reune tablas en un diccionario
outputs_tables = {
    "subnacional-desagregacion" : subnacional_desagregacion.to_pandas(),
    "subnacional-departamentos" : ajusta_df(subnacional_departamentos), 
    "nivel-subnacional-departamentos" : ajusta_df(nivel_subnacional_departamentos), 
    "tc-interanual-subnacional-departamentos" : ajusta_df(subnacional_departamentos_departamentos)
}

#### Exportamos tablas a GS
console.print("3.-", "Exportamos Tablas a GS", style="bold red")

for sheet_name, worksheet in worksheets.items():
    # Upload data (headers + values)
    worksheet.update(
        [outputs_tables[sheet_name].columns.values.tolist()] + outputs_tables[sheet_name].values.tolist()
    )

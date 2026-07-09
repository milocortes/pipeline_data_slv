## GS packages
import gspread
from google.oauth2.service_account import Credentials

## Disable Warnings
import warnings
warnings.filterwarnings("ignore")

## Carga rich
from rich.console import Console
console = Console()

## Carga lista de Tablas en GS
from utils import build_general_config, build_storage_config

import polars as pl
import pandas as pd
import numpy as np
import os

## Carga configuración
## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()


# Authenticate
console.print("1.-", "Autenticando en GS", style="bold red")

GS_API_KEY_FILE = os.getenv("GS_API_KEY_FILE")

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(f'config/api_keys/{GS_API_KEY_FILE}', scopes=scopes)
client = gspread.authorize(creds)

# Open Google Sheet and update
SPREADSHEET = os.getenv("GS_SPREADSHEET")
sh = client.open(SPREADSHEET)

tablas_actualizar_ive = [
    "nivel-historico-media-pronostico-modelos-lineales",
    "tc-interanual-historico-pronostico-modelos-lineal",
    "valores-obs-vs-pronostico-nivel-modelos-lineales",
    "valores-obs-vs-pronostico-tc-anual-mod-lineales",
    "nivel-historico-pronostico-modelos-ml", 
    "tc-interanual-historico-pronostico-modelos-ml"
]

# Carga IVE actualizado
ive = pl.read_delta(
        f"s3://{config['BUCKET_NAME']}/indice_vol_encad",
        storage_options=storage_options,
    ).with_columns(
        ## Ajustamos fecha del trimestre para que indique el último día del trimestre
        pl.col("datetime")
            .dt.truncate("1q")
            .dt.offset_by("2mo")
            .dt.month_end().dt.strftime("%Y-%m-%d"),
    )

# Construimos serie de crecimiento interanual original
ive_interanual = ive.rename({"datetime" : "Date"}).with_columns(
    (
        (pl.col("indice_vol_encad")/pl.col("indice_vol_encad").shift(4))-1
    ).round(4)
    
    )

####----------------------------------------------- ####
# nivel-historico-media-pronostico-modelos-lineales
####----------------------------------------------- ####

nivel_historico_media_pronostico_modelos_lineales = pl.read_delta(
        f"s3://{config['BUCKET_RESPALDO']}/nivel-historico-media-pronostico-modelos-lineales",
        storage_options=storage_options,
    )

nivel_historico_media_pronostico_modelos_lineales = (
    nivel_historico_media_pronostico_modelos_lineales.join(
        ive.rename(
            {
                "datetime" : "Date", 
                "indice_vol_encad" : "Histórico"
            }
        ), 
        on="Date", how="left", suffix="_new")
    .with_columns(
        pl.coalesce("Histórico_new", "Histórico").alias("Histórico")
    )
    .drop("Histórico_new")
).to_pandas()

## Imputamos el valor histórico del último trimestre observado a todas las columnas numericas
nivel_historico_media_pronostico_modelos_lineales.iloc[-2, 2:] = nivel_historico_media_pronostico_modelos_lineales.iloc[-2, 1]

####----------------------------------------------- ####
# tc-interanual-historico-pronostico-modelos-lineal
####----------------------------------------------- ####

tc_interanual_historico_pronostico_modelos_lineal = pl.read_delta(
        f"s3://{config['BUCKET_RESPALDO']}/tc-interanual-historico-pronostico-modelos-lineal",
        storage_options=storage_options,
    )

tc_interanual_historico_pronostico_modelos_lineal = (
    tc_interanual_historico_pronostico_modelos_lineal.join(
        ive_interanual.rename(
            {
                "indice_vol_encad" : "Histórico"
            }
        ), 
        on="Date", how="left", suffix="_new")
    .with_columns(
        pl.coalesce("Histórico_new", "Histórico").alias("Histórico")
    )
    .drop("Histórico_new")
).to_pandas()

## Imputamos el valor histórico del último trimestre observado a todas las columnas numericas
tc_interanual_historico_pronostico_modelos_lineal.iloc[-2, 2:] = tc_interanual_historico_pronostico_modelos_lineal.iloc[-2, 1]

####----------------------------------------------- ####
# valores-obs-vs-pronostico-nivel-modelos-lineales
####----------------------------------------------- ####

valores_obs_vs_pronostico_nivel_modelos_lineales = pl.read_delta(
        f"s3://{config['BUCKET_RESPALDO']}/valores-obs-vs-pronostico-nivel-modelos-lineales",
        storage_options=storage_options,
    )

valores_obs_vs_pronostico_nivel_modelos_lineales = (
    valores_obs_vs_pronostico_nivel_modelos_lineales.join(
        ive.rename(
            {
                "datetime" : "Date", 
                "indice_vol_encad" : "valor_observado_nivel"
            }
        ), 
        on="Date", how="left", suffix="_new")
    .with_columns(
        pl.coalesce("valor_observado_nivel_new", "valor_observado_nivel").alias("valor_observado_nivel")
    )
    .drop("valor_observado_nivel_new")
).to_pandas()

####----------------------------------------------- ####
# valores-obs-vs-pronostico-tc-anual-mod-lineales
####----------------------------------------------- ####

valores_obs_vs_pronostico_tc_anual_mod_lineales = pl.read_delta(
        f"s3://{config['BUCKET_RESPALDO']}/valores-obs-vs-pronostico-tc-anual-mod-lineales",
        storage_options=storage_options,
    )

valores_obs_vs_pronostico_tc_anual_mod_lineales = (
    valores_obs_vs_pronostico_tc_anual_mod_lineales.join(
        ive_interanual.rename(
            {
                "indice_vol_encad" : "valor_observado_tc_interanual"
            }
        ), 
        on="Date", how="left", suffix="_new")
    .with_columns(
        pl.coalesce("valor_observado_tc_interanual_new", "valor_observado_tc_interanual").alias("valor_observado_tc_interanual")
    )
    .drop("valor_observado_tc_interanual_new")
).to_pandas()

####----------------------------------------------- ####
# nivel-historico-pronostico-modelos-ml
####----------------------------------------------- ####

nivel_historico_pronostico_modelos_ml = pl.read_delta(
        f"s3://{config['BUCKET_RESPALDO']}/nivel-historico-pronostico-modelos-ml",
        storage_options=storage_options,
    )

def actualiza_niveles_ml(
        datos : pl.DataFrame
    ) -> pd.DataFrame: 
    datos_pre = (
        nivel_historico_pronostico_modelos_ml.join(
            ive.rename(
                {
                    "datetime" : "Date", 
                    "indice_vol_encad" : "Histórico"
                }
            ), 
            on="Date", how="left", suffix="_new")
        .with_columns(
            pl.coalesce("Histórico_new", "Histórico").alias("Histórico")
        )
        .drop("Histórico_new")
    ).to_pandas()

    ## Imputamos el valor histórico del último trimestre observado a todas las columnas numericas
    datos_pre.iloc[-2, 3:] = datos_pre.iloc[-2, 2]

    return datos_pre

nivel_historico_pronostico_modelos_ml = pd.concat([actualiza_niveles_ml(nivel_historico_pronostico_modelos_ml.filter(Modelo=modelo)) for modelo in nivel_historico_pronostico_modelos_ml["Modelo"].unique()])

####----------------------------------------------- ####
# tc-interanual-historico-pronostico-modelos-ml
####----------------------------------------------- ####

tc_interanual_historico_pronostico_modelos_ml = pl.read_delta(
        f"s3://{config['BUCKET_RESPALDO']}/tc-interanual-historico-pronostico-modelos-ml",
        storage_options=storage_options,
    )


def actualiza_tc_interanual_ml(
        datos : pl.DataFrame
    ) -> pd.DataFrame: 
    datos_pre = (
        tc_interanual_historico_pronostico_modelos_ml.join(
            ive_interanual.rename(
                {
                    "indice_vol_encad" : "Histórico"
                }
            ), 
            on="Date", how="left", suffix="_new")
        .with_columns(
            pl.coalesce("Histórico_new", "Histórico").alias("Histórico")
        )
        .drop("Histórico_new")
    ).to_pandas()

    ## Imputamos el valor histórico del último trimestre observado a todas las columnas numericas
    datos_pre.iloc[-2, 3:] = datos_pre.iloc[-2, 2]

    return datos_pre

tc_interanual_historico_pronostico_modelos_ml = pd.concat([actualiza_tc_interanual_ml(tc_interanual_historico_pronostico_modelos_ml.filter(Modelo=modelo)) for modelo in tc_interanual_historico_pronostico_modelos_ml["Modelo"].unique()])

#### Reunimos los datos
tablas_actualizadas = {
    "nivel-historico-media-pronostico-modelos-lineales" : nivel_historico_media_pronostico_modelos_lineales.replace(np.nan,""), 
    "tc-interanual-historico-pronostico-modelos-lineal" : tc_interanual_historico_pronostico_modelos_lineal.replace(np.nan,""),
    "valores-obs-vs-pronostico-nivel-modelos-lineales" : valores_obs_vs_pronostico_nivel_modelos_lineales.replace(np.nan,""),
    "valores-obs-vs-pronostico-tc-anual-mod-lineales" : valores_obs_vs_pronostico_tc_anual_mod_lineales.replace(np.nan,""),
    "nivel-historico-pronostico-modelos-ml" : nivel_historico_pronostico_modelos_ml.replace(np.nan,""),
    "tc-interanual-historico-pronostico-modelos-ml" : tc_interanual_historico_pronostico_modelos_ml.replace(np.nan,""),
}

#### Exportamos tablas a GS
console.print("6.-", "Exportamos Tablas a GS", style="bold red")

# Diccionario de tabs de Google Sheet
worksheets = {sheet : sh.worksheet(sheet) for sheet in tablas_actualizadas.keys()}


for sheet_name, worksheet in worksheets.items():
    # Upload data (headers + values)
    worksheet.update(
        [tablas_actualizadas[sheet_name].columns.values.tolist()] + tablas_actualizadas[sheet_name].values.tolist()
    )

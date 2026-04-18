import tomllib
from pathlib import Path
import polars as pl
import pandas as pd
import statsmodels.tsa.x13 as x13
import statsmodels.api as sm
from typing import List, Dict
import numpy as np 

## GS packages
import gspread
from google.oauth2.service_account import Credentials

## Disable Warnings
import warnings
warnings.filterwarnings("ignore")

## Carga configuración
FP = Path(".")

## Carga configuración general
with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

# 1. Authenticate
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('config/api_keys/pronosticos-493700-56f57502ffb3.json', scopes=scopes)
client = gspread.authorize(creds)

# 3. Open Google Sheet and update
sh = client.open("test_pronostico")

# Diccionario de tabs de Google Sheet
sheets = [
            "pronosticos-modelos-lineales", 
            "media-pronosticos-modelos-lineales", 
            "nivel-historico-media-pronostico-modelos-lineales", 
            "tc-interanual-historico-pronostico-modelos-lineal"
        ]

worksheets = {sheet : sh.worksheet(sheet) for sheet in sheets}


## Lista de Covariables
covariables = ['consumo_elect_al_publico', 'consumo_elect_comercio', 'consumo_elect_industria',
 'consumo_elect_total', 'evi_gee', 'ndvi_gee', 'precip', 'remesas_usd_trim', 'temp_ls', 'viirs_bm_sum', 'gdp_us_const_trim']

## Variable de respuesta
respuesta = "indice_vol_encad"

## Consolidamos tablas
datos = pl.concat([
    pl.read_delta(
        f"s3://{config['BUCKET_NAME']}/{cov}",
        storage_options=storage_options,
    )
    for cov in covariables + [respuesta]
],  how = "align")

## Transformamos datos
datos = datos.with_columns(
    pl.col(respuesta).log().alias(respuesta)
)

# Filtramos los valores para el trimestre posterior al último valor disponible del IVE
datos = datos.filter(
    pl.col("datetime") <= pl.col("datetime").filter(
        pl.col(respuesta).is_not_null()
    ).max().dt.offset_by("3mo")
)

# Desestacionalizamos para el Periodo 2012Q1-2024Q1
datos_P1 = datos.filter(
                pl.col("datetime") <= pl.datetime(2024,1,1)
            ).to_pandas().set_index("datetime")

for cov_des in covariables:
        datos_P1[cov_des] = x13.x13_arima_analysis(
            datos_P1[cov_des], freq = 4, x12path= "/usr/bin/x13as"#x12path="/home/milo/Documents/egtp/iniciativas/x13as/x13as_ascii"
        ).seasadj.to_numpy()

# Concatenamos con el Periodo >2024Q1
datos_P2 = datos.filter(
                pl.col("datetime") > pl.datetime(2024,1,1)
            ).to_pandas().set_index("datetime")

datos = pd.concat(
    [datos_P1, datos_P2]
)
datos

## Modelos
modelos = {
            "M1" : ["ndvi_gee", "evi_gee", "temp_ls", "precip", "remesas_usd_trim","consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
            "M2" : ["viirs_bm_sum", "temp_ls", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
            "M3" : ["temp_ls", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
            "M4" : ["viirs_bm_sum", "temp_ls", "precip", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
            "M5" : ["temp_ls", "precip", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
        }

### Función que calcula la tasa de crecimiento interanual para un modelo dado
def forecast(
    respuesta : str, 
    covariables : List[str], 
    modelo : str,
    datos : pd.DataFrame, 
    )-> Dict[str, pl.DataFrame]: 

    # Define variable de respuesta y covariables
    endog = datos[respuesta]
    exog = sm.add_constant(datos[covariables])
    
    # Fit the model
    mod = sm.tsa.statespace.SARIMAX(endog, exog, order=(1,0,2))
    res = mod.fit(disp=False)

    # In-sample one-step-ahead predictions
    predict = res.get_prediction()

    # Reunimos prediccione e intervalos de confianza
    prediccion_nivel = np.exp(predict.predicted_mean.loc['2012Q1':])
    prediccion = prediccion_nivel.reset_index().rename(columns= {"index" : "datetime"})

    # Cargamos originales
    ive = pl.read_delta(
            f"s3://{config['BUCKET_NAME']}/{respuesta}",
            storage_options=storage_options,
        )
    
    # Reunimos observados y pronosticados
    prediccion = pl.from_pandas(prediccion).with_columns(
        pl.col("datetime").dt.cast_time_unit("us")
    )
    
    # Calculamos el crecimiento interanual
    prediccion_modelo = pl.concat(
        [ive, prediccion], how = "align"
    ).with_columns(
        ### Calcula tasa de crecimiento interanual `prediccion_tc_interanual`
        (
            (
                (
                    pl.col("predicted_mean")/pl.col("indice_vol_encad").shift(4)
                ) - 1
            )#*100
        ).alias("prediccion_tc_interanual"),

        ### Calcula tasa de crecimiento trimestral `prediccion_tc_trimestral`
        (
            (
                (
                    pl.col("predicted_mean")/pl.col("indice_vol_encad").shift(1)
                ) - 1
            )#*100
        ).alias("prediccion_tc_trimestral"),

        ### Renombra pronóstico del nivel `prediccion_nivel`
        pl.col("predicted_mean").alias("prediccion_nivel"),

        ### Agrega columna del Modelo pronosticado
        pl.lit(modelo).alias("Modelo"), 

        ### Renombramos datime to date
        pl.col("datetime").alias("Date")
 
    ).select(
        "Date", "Modelo", "prediccion_tc_trimestral", "prediccion_tc_interanual", "prediccion_nivel"
    ).tail(1)#.with_columns(
        #pl.col("Date")
        #    .dt.truncate("1q")
        #    .dt.offset_by("2mo")
        #    .dt.month_end().dt.strftime("%Y-%m-%d")
        #)



    return prediccion_modelo

# pronosticos-modelos-lineales
predicciones_modelos = pl.concat(
        [forecast(respuesta, modelos[f"M{i}"], f"Modelo lineal {i}", datos) for i in range(1,6)]
    )
predicciones_modelos

# media-pronosticos-modelos-lineales
predicciones_medias = predicciones_modelos.group_by("Date").agg(
        pl.col("prediccion_tc_trimestral").mean(),
        pl.col("prediccion_tc_interanual").mean(),
        pl.col("prediccion_nivel").mean(),
    )
predicciones_medias

# nivel-historico-media-pronostico-modelos-lineales
# Cargamos originales
ive = pl.read_delta(
        f"s3://{config['BUCKET_NAME']}/{respuesta}",
        storage_options=storage_options,
    )


nivel_historico_media_lineales = pl.concat([ive.rename({"datetime" : "Date"}), predicciones_medias.select("Date", "prediccion_nivel")], how = "align").to_pandas()
nivel_historico_media_lineales.iloc[-2, 2] = nivel_historico_media_lineales.iloc[-2, 1]
nivel_historico_media_lineales = pl.from_pandas(nivel_historico_media_lineales)
nivel_historico_media_lineales

# tc-interanual-historico-pronostico-modelos-lineal
# Cargamos originales
ive_interanual = ive.rename({"datetime" : "Date"}).with_columns((pl.col("indice_vol_encad")/pl.col("indice_vol_encad").shift(4))-1)
tc_interanual_historico_lineales = pl.concat([ive_interanual, predicciones_medias.select("Date", "prediccion_tc_interanual")], how = "align").to_pandas()
tc_interanual_historico_lineales.iloc[-2, 2] = tc_interanual_historico_lineales.iloc[-2, 1]
tc_interanual_historico_lineales = pl.from_pandas(tc_interanual_historico_lineales)
tc_interanual_historico_lineales

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

outputs_tables = {
    "pronosticos-modelos-lineales" : ajusta_df(predicciones_modelos), 
    "media-pronosticos-modelos-lineales" : ajusta_df(predicciones_medias), 
    "nivel-historico-media-pronostico-modelos-lineales" : ajusta_df(nivel_historico_media_lineales), 
    "tc-interanual-historico-pronostico-modelos-lineal" : ajusta_df(tc_interanual_historico_lineales)
}

#### Exportamos tablas a GS
for sheet_name, worksheet in worksheets.items():
    # Upload data (headers + values)
    worksheet.update(
        [outputs_tables[sheet_name].columns.values.tolist()] + outputs_tables[sheet_name].values.tolist()
    )



import tomllib
from pathlib import Path
import polars as pl
import pandas as pd
import statsmodels.tsa.x13 as x13
import statsmodels.api as sm
from typing import List, Dict
import numpy as np 
import polars.selectors as cs

## Cargamos rutina de pronóstico
from utils import train_and_forecast, get_SHAP

## GS packages
import gspread
from google.oauth2.service_account import Credentials

## Disable Warnings
import warnings
warnings.filterwarnings("ignore")

## Carga rich
from rich.console import Console
console = Console()

## Carga configuración
FP = Path(".")

## Carga configuración general
with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

# 1. Authenticate
console.print("1.-", "Autenticando en GS", style="bold red")

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('config/api_keys/pronosticos-493700-56f57502ffb3.json', scopes=scopes)
client = gspread.authorize(creds)

# 3. Open Google Sheet and update
sh = client.open("insumos-tablero-pib")

# Diccionario de tabs de Google Sheet
sheets = [
            "pronosticos-modelos-lineales", 
            "media-pronosticos-modelos-lineales", 
            "nivel-historico-media-pronostico-modelos-lineales", 
            "tc-interanual-historico-pronostico-modelos-lineal", 
            "valores-obs-vs-pronostico-nivel-modelos-lineales", 
            "valores-obs-vs-pronostico-tc-anual-mod-lineales", 
            "info-tabla-contribucion-variables-modelos-lineales"   
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

# Filtramos los valores para el trimestre posterior al último valor disponible del IVE
datos = datos.filter(
    pl.col("datetime") <= pl.col("datetime").filter(
        pl.col(respuesta).is_not_null()
    ).max().dt.offset_by("3mo")
)

## Creamos una copia del dataframe
data_set_cov = datos.clone().to_pandas().set_index("datetime")

console.print("2.-", "Desestacionalizando series", style="bold red")

### Desestacionalizamos covariables
for cov_des in covariables:
        data_set_cov[cov_des] = x13.x13_arima_analysis(
            data_set_cov[cov_des], freq = 4#, x12path= "/usr/bin/x13as"#x12path="/home/milo/Documents/egtp/iniciativas/x13as/x13as_ascii"
        ).seasadj.to_numpy()

data_set_cov = pl.from_pandas(data_set_cov.reset_index())

#### TRANSFORMAMOS DATOS
### Calculamos la primera diferencia de la variable respuesta (logaritmo del IVE) y covariables
### Usemos Expression expansion de Polars
### Expression expansion is a Polars feature that lets you write short but powerful expressions whilst avoiding structural repetition. When you want to write the same expression for multiple columns, you can write a single expression that Polars will expand into multiple parallel expressions.

data_set_cov = data_set_cov.with_columns(
    (pl.col([respuesta] + covariables)/pl.col([respuesta] + covariables).shift(1)).log()
).to_pandas().set_index("datetime").loc["2012Q2":]

## Modelos
modelos = {
            "M1" : ["ndvi_gee", "evi_gee", "temp_ls", "precip", "remesas_usd_trim","consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
            "M2" : ["viirs_bm_sum", "temp_ls", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
            "M3" : ["temp_ls", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
            "M4" : ["viirs_bm_sum", "temp_ls", "precip", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
            "M5" : ["temp_ls", "precip", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
        }

## Definimos Train, Test y último valor disponible del IVE en niveles
target = data_set_cov[respuesta]
exog = data_set_cov[covariables]
ive_nivel = datos["indice_vol_encad"].to_numpy()[-2]

####----------------------------------------------- ####
# pronosticos-modelos-lineales
####----------------------------------------------- ####

## Reunimos pronósticos

console.print("3.-", "Entrenando y Generando pronósticos de los Modelos Lineales ARIMAX", style="bold red")

predicciones_modelos = pd.concat(
                [
                    train_and_forecast(target, exog, modelo, modelos[modelo], ive_nivel) for modelo in modelos
                ], ignore_index=True
            )

console.print("4.-", "Construyendo Tablas para GS", style="bold red")

## Agregamos valor del IVE del trimestre anterior
predicciones_modelos["trimestre_anterior"] = datos.to_pandas()["indice_vol_encad"].iloc[-2]
predicciones_modelos["trimestre_anual_anterior"] = datos.to_pandas()["indice_vol_encad"].iloc[-5]

## Calcula crecimiento interanual
predicciones_modelos = pl.from_pandas(predicciones_modelos)
predicciones_modelos = predicciones_modelos.with_columns(
    ### Calculamos crecimiento interanual
    prediccion_tc_interanual = 
    (
        (
            pl.col("prediccion_nivel")/pl.col("trimestre_anual_anterior")
        ) -1 
    ), 
    ### Calculamos crecimiento trimestral
    prediccion_tc_trimestral = 
    (
        (
            pl.col("prediccion_nivel")/pl.col("trimestre_anterior")
        ) -1 
    ), 
).with_columns(
    pl.col("Date").cast(pl.Datetime("us"))
).select("Date", "Modelo", "prediccion_tc_trimestral", "prediccion_tc_interanual", "prediccion_nivel")

####----------------------------------- ####
# media-pronosticos-modelos-lineales
####----------------------------------- ####

predicciones_medias = predicciones_modelos.group_by("Date").agg(
        ### Cálculo de los valores medios para los 5 modelos
        pl.col("prediccion_tc_trimestral").mean(),
        pl.col("prediccion_tc_interanual").mean(),
        pl.col("prediccion_nivel").mean(),
        
        ### Cálculo de los límites inferiores
        pl.col("prediccion_nivel").min().alias("lim_inf_prediccion_nivel"), 
        pl.col("prediccion_tc_interanual").min().alias("lim_inf_prediccion_tc_interanual"), 

        ### Cálculo de los límites superiores
        pl.col("prediccion_nivel").max().alias("lim_sup_prediccion_nivel"), 
        pl.col("prediccion_tc_interanual").max().alias("lim_sup_prediccion_tc_interanual"), 
    )
predicciones_medias

####----------------------------------------------- ####
# nivel-historico-media-pronostico-modelos-lineales
####----------------------------------------------- ####

# Cargamos originales
ive = pl.read_delta(
        f"s3://{config['BUCKET_NAME']}/{respuesta}",
        storage_options=storage_options,
    )

## Construimos dataframe
nivel_historico_media_lineales = pl.concat(
                                        [   
                                            ## Agregamos valor histórico del IVE
                                            ive.rename({"datetime" : "Date"}), 
                                            ## Agregamos media del pronóstico del IVE en nivel para los 5 Modelos
                                            predicciones_medias.select("Date", "prediccion_nivel"), 
                                            ## Agregamos limite inferior del pronóstico del IVE
                                            predicciones_medias.select("Date", "lim_inf_prediccion_nivel"), 
                                            ## Agregamos limite superior del pronóstico del IVE
                                            predicciones_medias.select("Date", "lim_sup_prediccion_nivel"),                                          
                                        ], how = "align"
                                ).to_pandas()

## Imputamos el valor histórico del último trimestre observado a todas las columnas numericas
nivel_historico_media_lineales.iloc[-2, 2:] = nivel_historico_media_lineales.iloc[-2, 1]
nivel_historico_media_lineales = pl.from_pandas(nivel_historico_media_lineales)
nivel_historico_media_lineales = nivel_historico_media_lineales.rename(
    {
        "indice_vol_encad" : "Histórico", 
        "prediccion_nivel" : "Media de pronósticos", 
        "lim_inf_prediccion_nivel" : "Límite inferior",
        "lim_sup_prediccion_nivel" : "Límite superior"
    }
)
nivel_historico_media_lineales

####----------------------------------------------- ####
# tc-interanual-historico-pronostico-modelos-lineal
####----------------------------------------------- ####

# Construimos serie de crecimiento interanual original
ive_interanual = ive.rename({"datetime" : "Date"}).with_columns((pl.col("indice_vol_encad")/pl.col("indice_vol_encad").shift(4))-1)

## Construimos dataframe
tc_interanual_historico_lineales = pl.concat(
                                        [
                                            ## Agregamos valor histórico del crecimiento interanual del IVE
                                            ive_interanual, 
                                            ## Agregamos media del pronóstico del crecimiento interanual del IVE para los 5 Modelos
                                            predicciones_medias.select("Date", "prediccion_tc_interanual"),
                                            ## Agregamos limite inferior pronóstico del crecimiento interanual del IVE
                                            predicciones_medias.select("Date", "lim_inf_prediccion_tc_interanual"), 
                                            ## Agregamos limite superior pronóstico del crecimiento interanual del IVE
                                            predicciones_medias.select("Date", "lim_sup_prediccion_tc_interanual"),                                                                                   
                                        ], how = "align"
                                ).to_pandas()

## Imputamos el valor histórico del último trimestre observado a todas las columnas numericas
tc_interanual_historico_lineales.iloc[-2, 2:] = tc_interanual_historico_lineales.iloc[-2, 1]
tc_interanual_historico_lineales = pl.from_pandas(tc_interanual_historico_lineales)
tc_interanual_historico_lineales = tc_interanual_historico_lineales.rename(
    {
        "indice_vol_encad" : "Histórico", 
        "prediccion_tc_interanual" : "Media de pronósticos", 
        "lim_inf_prediccion_tc_interanual" : "Límite inferior",
        "lim_sup_prediccion_tc_interanual" : "Límite superior"
    }
)
tc_interanual_historico_lineales

####----------------------------------------------- ####
# valores-obs-vs-pronostico-nivel-modelos-lineales
####----------------------------------------------- ####
### Cargamos tabla con los valores pronosticados del IVE en nivel
arimax_pronostico_nivel = pl.read_delta(
        f"s3://{config['BUCKET_NAME']}/arimax_pronostico_nivel",
        storage_options=storage_options,
    )

### La tabla tiene los pronósticos hasta el trimestre anterior al actualmente pronosticado
### En primera instancia, agregaremos el pronóstico del trimestre actual a la tabla y la actualizaremos en 
### Delta Lake alojado en RustFS
arimax_pronostico_nivel = pl.concat(
    [
        arimax_pronostico_nivel, 
        predicciones_medias.select("Date", "prediccion_nivel").rename({"prediccion_nivel" : "media_prediccion_nivel"})
    ]
).unique(
    keep='last' ### En caso de valor duplicado, nos quedamos con el último valor observado
).sort(
    by = "Date"
)

### Actualizamos tabla
arimax_pronostico_nivel.write_delta(
    f"s3://{config['BUCKET_NAME']}/arimax_pronostico_nivel",
    storage_options=storage_options,
    mode = "overwrite"
)

### Obtenemos el valor observado del IVE en nivel para el periodo que disponemos de pronósticos
### Para construir la tabla valores-obs-vs-pronostico-nivel-modelos-lineales

obs_vs_pronostico_nivel_arimax = arimax_pronostico_nivel.join(
    ive.rename(
        {
            "datetime" : "Date", 
            "indice_vol_encad" : "valor_observado_nivel"
        }), 
    on = "Date", 
    how = "left"
).select(
    "Date", "valor_observado_nivel", "media_prediccion_nivel"
).with_columns(
    cs.float().round(3) # Redondeamos a tres digitos
)



####----------------------------------------------- ####
# valores-obs-vs-pronostico-tc-anual-mod-lineales
####----------------------------------------------- ####
### Cargamos tabla con los valores pronosticados de la tasa de crecimiento interanual del IVE
arimax_pronostico_tc_interanual = pl.read_delta(
        f"s3://{config['BUCKET_NAME']}/arimax_pronostico_tc_interanual",
        storage_options=storage_options,
    )

### La tabla tiene los pronósticos del crecimiento interanual hasta el trimestre anterior al actualmente pronosticado
### En primera instancia, agregaremos el pronóstico del crecimiento interanual trimestre actual a la tabla y la actualizaremos en 
### Delta Lake alojado en RustFS
arimax_pronostico_tc_interanual = pl.concat(
    [
        arimax_pronostico_tc_interanual, 
        predicciones_medias.select("Date", "prediccion_tc_interanual").rename({"prediccion_tc_interanual" : "media_prediccion_tc_interanual"})
    ]
).unique(
    keep='last' ### En caso de valor duplicado, nos quedamos con el último valor observado
).sort(
    by = "Date"
)

### Actualizamos tabla
arimax_pronostico_tc_interanual.write_delta(
    f"s3://{config['BUCKET_NAME']}/arimax_pronostico_tc_interanual",
    storage_options=storage_options,
    mode = "overwrite"
)

### Obtenemos el valor observado del crecimiento interanual del IVE para el periodo que disponemos de pronósticos
### Para construir la tabla valores-obs-vs-pronostico-tc-anual-mod-lineales
obs_vs_pronostico_tc_anual_arimax = arimax_pronostico_tc_interanual.join(
    ive_interanual.rename(
        {
            "indice_vol_encad" : "valor_observado_tc_interanual"
        }), 
    on = "Date", 
    how = "left"
).select(
    "Date", "valor_observado_tc_interanual", "media_prediccion_tc_interanual"
).with_columns(
    cs.float().round(3) # Redondeamos a tres digitos
)


####----------------------------------------------- ####
# info-tabla-contribucion-variables-modelos-lineales
####----------------------------------------------- ####
contribucion_covariables_modelos = pd.concat(
                [
                    get_SHAP(target, exog, modelo, modelos[modelo]) for modelo in modelos
                ], ignore_index=True
            )

contribucion_covariables_modelos["Contribución"] = contribucion_covariables_modelos["Contribución"].round(2)

#### Guardamos dataframes de salida en un diccionario
def ajusta_df(
    datos : pl.DataFrame
    ) -> pd.DataFrame:
    return datos.with_columns(
        ## Ajustamos fecha del trimestre para que indique el último día del trimestre
        pl.col("Date")
            .dt.truncate("1q")
            .dt.offset_by("2mo")
            .dt.month_end().dt.strftime("%Y-%m-%d"),
        ## Redondeamos a 3 dígitos los valores numéricos
         cs.float().round(3)
        ).to_pandas().replace(np.nan, "")

##### Ajustamos nombres de columnas de la tabla de predicciones_medias
predicciones_medias = predicciones_medias.select(
    "Date", "prediccion_tc_trimestral", "prediccion_tc_interanual", "prediccion_nivel"
).rename(
    {
        "prediccion_tc_trimestral" : "media_prediccion_tc_trimestral", 
        "prediccion_tc_interanual" : "media_prediccion_tc_interanual", 
        "prediccion_nivel" : "media_prediccion_nivel"
    }
)

### Reune tablas en un diccionario
outputs_tables = {
    "pronosticos-modelos-lineales" : ajusta_df(predicciones_modelos), 
    "media-pronosticos-modelos-lineales" : ajusta_df(predicciones_medias), 
    "nivel-historico-media-pronostico-modelos-lineales" : ajusta_df(nivel_historico_media_lineales), 
    "tc-interanual-historico-pronostico-modelos-lineal" : ajusta_df(tc_interanual_historico_lineales), 
    "valores-obs-vs-pronostico-nivel-modelos-lineales" : ajusta_df(obs_vs_pronostico_nivel_arimax), 
    "valores-obs-vs-pronostico-tc-anual-mod-lineales" : ajusta_df(obs_vs_pronostico_tc_anual_arimax), 
    "info-tabla-contribucion-variables-modelos-lineales" : contribucion_covariables_modelos
}

#### Exportamos tablas a GS
console.print("5.-", "Exportamos Tablas a GS", style="bold red")

for sheet_name, worksheet in worksheets.items():
    # Upload data (headers + values)
    worksheet.update(
        [outputs_tables[sheet_name].columns.values.tolist()] + outputs_tables[sheet_name].values.tolist()
    )

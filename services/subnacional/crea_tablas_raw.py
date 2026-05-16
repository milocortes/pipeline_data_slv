import pandas as pd
import tomllib
from pathlib import Path
import polars as pl

## Carga configuración
FP = Path(".")

## Carga configuración general
with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

### Extraemos la información de los archivos excel panel_data_subnacional.xlsx y panel_data_subnacional_forecast.xlsx
xls = pd.ExcelFile('datos/raw/panel_data_subnacional.xlsx')

# returns a list of strings
sheet_names = xls.sheet_names

COLUMNAS = {
                "Unnamed: 0" : "datetime", 
                "gdp" : "gdp_ppp_departamento",
                "electricidad" : "electricidad_departamento", 
                "viirs" : "viirs_bm_sum_departamento", 
            }

acumula = []

for sheet in sheet_names:
    df_historico = pd.read_excel("datos/raw/panel_data_subnacional.xlsx", sheet_name=sheet).drop(columns = "pop")
    df_pronostico = pd.read_excel("datos/raw/panel_data_subnacional_forecast.xlsx", sheet_name=sheet).drop(columns = "pop")

    df_historico = df_historico.rename(columns = COLUMNAS)
    df_pronostico = df_pronostico.rename(columns = COLUMNAS)

    df_historico["GID_1"] = sheet
    df_pronostico["GID_1"] = sheet

    df = pd.concat([df_historico, df_pronostico], ignore_index = True)

    acumula.append(
        df
    )

datos = pd.concat(acumula, ignore_index = True)

covariables = ["gdp_ppp_departamento", "electricidad_departamento", "viirs_bm_sum_departamento"]

for cov in covariables:
    data_cov = datos[["datetime", "GID_1", cov]]
    data_cov.to_csv(f"datos/{cov}.csv", index = False)


### Cargamos las tablas nuevamente para guardarlas en Delta Lake
covariables += ["poblacion_departamento"]

for cov in covariables:
    data_cov = pl.read_csv(f"datos/{cov}.csv")
    data_cov.write_delta(
    f"s3://{config['BUCKET_NAME']}/{cov}",
    storage_options=storage_options,
    mode = "overwrite"
)


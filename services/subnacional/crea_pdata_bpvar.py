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

## Definimos covariables
covariables = ["gdp_ppp_departamento", "electricidad_departamento", "viirs_bm_sum_departamento", "poblacion_departamento"]


## Lee tablas
lee_tabla = lambda cov :  pl.read_delta(
        f"s3://{config['BUCKET_NAME']}/{cov}",
        storage_options=storage_options,
    )

#### ----------------------- ###
####  Covariables Endógenas
#### ----------------------- ###

gdp = lee_tabla("gdp_ppp_departamento")
electricidad = lee_tabla("electricidad_departamento")
viirs = lee_tabla("viirs_bm_sum_departamento")
pob = lee_tabla("poblacion_departamento").with_columns(
    pl.col("poblacion_departamento").log()
)

#### ----------------------- ###
####  Covariables Exógenas
#### ----------------------- ###
remesas = lee_tabla("remesas_usd_trim")


#### --------------------------------------- ###
####  Consolida tabla Covariables Endógenas
#### --------------------------------------- ###
 
datos = gdp.join(
    pob, on = ["datetime", "GID_1"]
).join(
    electricidad, on = ["datetime", "GID_1"]
).join(
    viirs, on = ["datetime", "GID_1"]
).with_columns(
    pl.col("datetime").str.to_datetime("%Y-%m-%d")
)

last_quarter = datos.select(pl.col("datetime").max()).item()

### Tabla con datos históricos
historico = datos.filter(
    (
        pl.col("datetime") >= pl.datetime(2012, 1, 1)
    ) &
    (
        pl.col("datetime") < pl.datetime(2023, 1, 1)
    )
).to_pandas()

### Tabla con datos del pronóstico
pronostico = datos.filter(
    pl.col("datetime") >= pl.datetime(2023, 1, 1) 
).to_pandas()

### Creamos el excel de insumo de datos históricos
with pd.ExcelWriter('panel_data_subnacional.xlsx') as writer:
    for gid in historico["GID_1"].unique():

        historico_dep = historico.query(
                            f"GID_1=='{gid}'"
                        ).drop(
                            columns = ["GID_1"]
                        ).set_index(
                            "datetime"
                        ).rename_axis('')

        historico_dep.to_excel(writer, sheet_name=gid, index=True)


### Creamos el excel de insumo de datos a pronosticar
with pd.ExcelWriter('panel_data_subnacional_forecast.xlsx') as writer:
    for gid in pronostico["GID_1"].unique():

        pronostico_dep = pronostico.query(
                            f"GID_1=='{gid}'"
                        ).drop(
                            columns = ["GID_1"]
                        ).set_index(
                            "datetime"
                        ).rename_axis('')

        pronostico_dep.to_excel(writer, sheet_name=gid, index=True)


#### --------------------------------------- ###
####  Consolida tabla Covariables Exógenas
#### --------------------------------------- ###
remesas = remesas.filter(pl.col("datetime") <= last_quarter)

### Tabla con datos históricos
remesas_historico = remesas.filter(
    (
        pl.col("datetime") >= pl.datetime(2012, 1, 1)
    ) &
    (
        pl.col("datetime") < pl.datetime(2023, 1, 1)
    )
).with_columns(
    pl.col("remesas_usd_trim").log()
).to_pandas()

### Tabla con datos del pronóstico
remesas_pronostico = remesas.filter(
    pl.col("datetime") >= pl.datetime(2023, 1, 1) 
).with_columns(
    pl.col("remesas_usd_trim").log()
).to_pandas()


### Creamos el excel de insumo de datos históricos
with pd.ExcelWriter('panel_data_subnacional_exo.xlsx') as writer:
    for gid in historico["GID_1"].unique():

        remesas_historico_dep = remesas_historico.set_index(
                            "datetime"
                        ).rename_axis('')

        remesas_historico_dep.to_excel(writer, sheet_name=gid, index=True)


### Creamos el excel de insumo de datos a pronosticar
with pd.ExcelWriter('panel_data_subnacional_exo_forecast.xlsx') as writer:
    for gid in pronostico["GID_1"].unique():

        remesas_pronostico_dep = remesas_pronostico.set_index(
                            "datetime"
                        ).rename_axis('')

        remesas_pronostico_dep.to_excel(writer, sheet_name=gid, index=True)


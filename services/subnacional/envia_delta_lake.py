## Carga paquetes
import tomllib
from pathlib import Path
import polars as pl
from deltalake import DeltaTable

## Carga configuración
FP = Path(".")

with open(FP/"config"/"general"/"config.toml", "rb") as f:
    config = tomllib.load(f)

## Carga Configuración de almacenamiento
with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
    storage_options = tomllib.load(f)

## Carga salidas del modelo BPVAR
datos = pl.read_csv(
            "pronostico_subnacional_departamentos.csv"
        ).with_columns(
            pl.col("datetime").str.to_datetime("%Y-%m-%d")
        ).with_columns(
            ## Exponenciamos los valores en logaritmos
            pl.col("mean").exp()
        )

## Creamos los ponderadores los cuales corresponden a los pesos relativos del GDP PPP de cada 
## Departamento en el total del GDP Nacional
gdp_ppp_nacional = datos.group_by(
                        "datetime"
                    ).agg(
                        pl.col("mean").sum()
                    ).rename({"mean" : "gdp_ppp_nacional"})

## Reunimos total nacional con los datos a nivel departamento
datos = datos.select(
    "datetime", "departamento", "mean"
).join(
    gdp_ppp_nacional, 
    on = "datetime", 
    how = "left"
).with_columns(
    ## Calculamos el ponderador
    ponderador = pl.col("mean")/pl.col("gdp_ppp_nacional")
).select(
    "datetime", "departamento", "ponderador"
)

## Construimos ruta de la tabla en el almacenamiento de objetos
URL_DELTA_TABLE = f"s3://{config['BUCKET_NAME']}/pronostico_subnacional_departamentos"

## Test si la tabla existe
if DeltaTable.is_deltatable(URL_DELTA_TABLE, storage_options=storage_options):
    
    ## La tabla existe, hacemos un upsert de los ponderadores departamentales
    ## Esto lo hacemos con la intención de mantener fijos los ponderadores calculados
    ## y no modificarlos cada vez que se reestime el modelo BPVAR
    datos_old = pl.read_delta(
                f"s3://{config['BUCKET_NAME']}/pronostico_subnacional_departamentos",
                storage_options=storage_options,
            )

    # Get only the rows in datos that do NOT exist in old_df
    nuevas_filas = datos.join(datos_old, on=["datetime", "departamento"], how="anti")

    # Concatenamos las filas en datos que no existen en los datos actuales
    datos = pl.concat(
                [datos_old, nuevas_filas]
            ).sort(
                by = ["departamento", "datetime"]
            )

    ## Guardamos la tabla de ponderadores en formato Delta Table en RustFS
    datos.write_delta(
        f"s3://{config['BUCKET_NAME']}/pronostico_subnacional_departamentos",
        storage_options=storage_options,
        mode = "overwrite"
    )


else:
    ## Guardamos por primera vez la tabla de ponderadores en formato Delta Table en RustFS
    datos.write_delta(
        f"s3://{config['BUCKET_NAME']}/pronostico_subnacional_departamentos",
        storage_options=storage_options,
        mode = "overwrite"
    )

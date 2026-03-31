import polars as pl 
from pathlib import Path

## Carga todas las tablas del Delta Lake
FP = Path(".")
FP_DL = FP/"delta_lake"

delta_tables = list(FP_DL.glob("*"))

## Función que construye crecimientos trimestrales e interanuales
def crecimientos(datos : pl.DataFrame, column_name : str):
    """
    Necesitamos una función que construya las siguientes transformaciones a la serie de tiempo (Se asume que la serie ya está en frecuencia trimestral n):
    - Crecimiento respecto al periodo previo (_g)
    - Crecimiento interanual (_int_g)
    """

    datos = datos.with_columns(
        ## Crecimiento respecto al periodo previo
        (pl.col(column_name).pct_change()*100).alias(f"{column_name}_g"), 
        ## Crecimiento interanual
        (pl.col(column_name).pct_change(n = 4)*100).alias(f"{column_name}_int_g"), 
    )

    return datos

### Iteramos para cada tabla en el Delta Lake
acumula = []

for tabla in delta_tables:
    tabla_var_name = str(tabla).split("/")[-1]

    df_tabla = crecimientos(
        pl.read_delta(tabla), 
        tabla_var_name
    )

    acumula.append(
        df_tabla
    )

## Concatenamos las tablas
datos = pl.concat(acumula, how = "align")

import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return


@app.cell
def _():
    import tomllib
    from pathlib import Path
    import polars as pl
    import pandas as pd
    import statsmodels.tsa.x13 as x13
    import numpy as np
    import statsmodels.api as sm
    import matplotlib.pyplot as plt

    return Path, np, pd, pl, plt, sm, tomllib, x13


@app.cell
def _(Path, tomllib):
    ## Carga configuración
    FP = Path(".")

    ## Carga configuración general
    with open(FP/"config"/"general"/"config.toml", "rb") as f:
        config = tomllib.load(f)

    ## Carga Configuración de almacenamiento
    with open(FP/"config"/"storage"/"storage_config.toml", "rb") as f:
        storage_options = tomllib.load(f)
    return config, storage_options


@app.cell
def _():
    ## Lista de Covariables
    covariables = ['consumo_elect_al_publico', 'consumo_elect_comercio', 'consumo_elect_industria',
     'consumo_elect_total', 'evi_gee', 'ndvi_gee', 'precip', 'remesas_usd_trim', 'temp_ls', 'viirs_bm_sum', 'gdp_us_const_trim']

    ## Variable de respuesta
    respuesta = "indice_vol_encad"
    return covariables, respuesta


@app.cell
def _(config, pl, storage_options):
    ## Carga datos faltantes
    datos_ana = pl.read_parquet("test_data_input/dataset_clean_slv_2025_Q4.parquet")

    ## Mandamos al bucket las tablas que nos hacen falta
    tablas_faltantes = ['consumo_elect_al_publico', 'consumo_elect_comercio', 'consumo_elect_industria', 'consumo_elect_total', 'viirs_bm_sum']

    ## Guardamos tablas
    for tb in tablas_faltantes:
        datos_ana.select("datetime", tb).write_delta(
        f"s3://{config['BUCKET_NAME']}/{tb}",
        storage_options=storage_options,
        mode = "overwrite"
    )
    return


@app.cell
def _(config, covariables, pd, pl, respuesta, storage_options, x13):
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
                datos_P1[cov_des], freq = 4, x12path="/home/milo/Documents/egtp/iniciativas/x13as/x13as_ascii"
            ).seasadj.to_numpy()

    # Concatenamos con el Periodo >2024Q1
    datos_P2 = datos.filter(
                    pl.col("datetime") > pl.datetime(2024,1,1)
                ).to_pandas().set_index("datetime")

    datos = pd.concat(
        [datos_P1, datos_P2]
    )
    datos
    return (datos,)


@app.cell
def _():
    modelos = {
                "M1" : ["ndvi_gee", "evi_gee", "temp_ls", "precip", "remesas_usd_trim","consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
                "M2" : ["viirs_bm_sum", "temp_ls", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
                "M3" : ["temp_ls", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
                "M4" : ["viirs_bm_sum", "temp_ls", "precip", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
                "M5" : ["temp_ls", "precip", "remesas_usd_trim", "consumo_elect_al_publico", "consumo_elect_comercio", "consumo_elect_industria", "consumo_elect_total"], 
            }
    return (modelos,)


@app.cell
def _(datos, modelo_id, modelos, respuesta, sm):
    # Variables
    endog = datos[respuesta]
    exog = sm.add_constant(datos[modelos[modelo_id]])

    # Fit the model
    mod = sm.tsa.statespace.SARIMAX(endog, exog, order=(1,0,2))
    res = mod.fit(disp=False)

    return (res,)


@app.cell
def _(res):
    # In-sample one-step-ahead predictions
    predict = res.get_prediction()
    predict_ci = predict.conf_int()
    return predict, predict_ci


@app.cell
def _(datos, plt, predict, predict_ci, respuesta):
    # Graph
    fig, ax = plt.subplots(figsize=(9,4))
    npre = 4
    ax.set(title='Indice de Volumen Encadenado', xlabel='Date', ylabel='Billions of dollars')

    # Plot data points
    datos[respuesta].plot(ax=ax, style='-', label='Observed')

    # Plot predictions
    predict.predicted_mean.loc['2012Q1':].plot(ax=ax, style='r--', label='One-step-ahead forecast')
    ci = predict_ci.loc['2012Q1':]
    ax.fill_between(ci.index, ci.iloc[:,0], ci.iloc[:,1], color='r', alpha=0.1)

    legend = ax.legend(loc='lower right')
    plt.show()
    return (ci,)


@app.cell
def _(ci, config, np, pd, pl, predict, respuesta, storage_options):
    # Reunimos prediccione e intervalos de confianza
    prediccion_nivel = np.exp(predict.predicted_mean.loc['2012Q1':])
    prediccion_lower = np.exp(ci.loc['2012Q1':, "lower indice_vol_encad"])
    prediccion_upper = np.exp(ci.loc['2012Q1':, "upper indice_vol_encad"])

    prediccion = pd.concat(
        [prediccion_nivel, prediccion_lower, prediccion_upper], axis = 1
    ).reset_index().rename(columns= {"index" : "datetime"})


    # Cargamos originales
    ive = pl.read_delta(
            f"s3://{config['BUCKET_NAME']}/{respuesta}",
            storage_options=storage_options,
        )

    # Reunimos observados y pronosticados
    prediccion = pl.from_pandas(prediccion).with_columns(
        pl.col("datetime").dt.cast_time_unit("us")
    )

    analiza = pl.concat(
        [ive, prediccion], how = "align"
    )

    analiza
    return (analiza,)


@app.cell
def _(analiza, pl):
    analiza.with_columns(
        pct_observado = ((pl.col("indice_vol_encad")/pl.col("indice_vol_encad").shift(4)) - 1)*100, 
        pct_mean = ((pl.col("predicted_mean")/pl.col("indice_vol_encad").shift(4)) - 1)*100, 
        pct_lower = ((pl.col("lower indice_vol_encad")/pl.col("indice_vol_encad").shift(4)) - 1)*100, 
        pct_upper = ((pl.col("upper indice_vol_encad")/pl.col("indice_vol_encad").shift(4)) - 1)*100, 
    ).select("datetime", "pct_observado", "pct_mean", "pct_lower", "pct_upper")
    return


@app.cell
def _():
    ((133.71/128.81)-1)*100
    return


@app.cell
def _(np):
    np.mean([7.2633651318562810, 4.3703489495974910, 2.9520718624918450, 6.7133047984659470, 6.7750299087157680]).round(1)
    return


@app.cell
def _(np):
    np.mean([2.5395288792302350, 3.8280017388206520, 3.0959646644215244, 4.1565921867625420, 2.2579726010736545]).round(1)
    return


@app.cell
def _():
    modelo_id = "M5"
    return (modelo_id,)


if __name__ == "__main__":
    app.run()

## Cargamos rutina SARIMAX
from statsmodels.tsa.statespace.sarimax import SARIMAX
from typing import List, Dict
import pandas as pd 
import numpy as np 
import shap 
import os

## Método que construye diccionarios con las variables de ambiente de la configuración general
def build_general_config() -> Dict[str,str]:
    return {
        "start_date" : os.getenv("start_date"), 
        "LSIB" : os.getenv("LSIB"), 
        "BUCKET_NAME" : os.getenv("BUCKET_NAME"), 
        "service_account_gee" : os.getenv("service_account_gee"), 
        "gee_project" : os.getenv("gee_project")
    }

## Método que construye diccionarios con las variables de ambiente de la configuración del storage
def build_storage_config() -> Dict[str,str]:
    return {
        'AWS_ENDPOINT_URL': os.getenv("AWS_ENDPOINT_URL"),
        'AWS_REGION': os.getenv("AWS_REGION"),
        'AWS_ACCESS_KEY_ID': os.getenv("AWS_ACCESS_KEY_ID"),
        'AWS_SECRET_ACCESS_KEY': os.getenv("AWS_SECRET_ACCESS_KEY"),
        'allow_http': os.getenv("allow_http")
    }

## Diccionarios con nombres completos de modelos
modelos_nombres = {f"M{i}" : f"Modelo lineal {i}"  for i in range(1,6)}

## Nombre completo de Covariables
long_name_covariables = {
    'consumo_elect_al_publico' : 'Consumo electrico trimestral agregado al publico en kWh', 
    'consumo_elect_comercio' : 'Consumo electrico trimestral agregado a comercios en kWh', 
    'consumo_elect_industria' : 'Consumo electrico trimestral agregado a industria en kWh', 
    'consumo_elect_total' : 'Consumo electrico trimestral agregado total en kWh', 
    'evi_gee' : 'EVI (Enhanced Vegetation Index)', 
    'ndvi_gee' : 'NDVI (Normalized Difference Vegetation Index)', 
    'precip' : 'Precipitacion (milímetros)', 
    'remesas_usd_trim' : 'Remesas trimestrales en millones de US$', 
    'temp_ls' : 'Temperatura de la superficie terrestre (°C)', 
    'viirs_bm_sum': 'Luces Nocturnas VIIRS Black Marble', 
    'gdp_us_const_trim' : 'GDP constante trimestral de EEUU'
}

def train_and_forecast( 
    target : pd.DataFrame, 
    exog : pd.DataFrame,
    modelo : str, 
    covariables : List[str], 
    ive_nivel : float
    ) -> pd.DataFrame: 

    ## Define conjunto de entrenamiento y prueba
    target_train = target.loc["2012Q2":"2018Q4"]
    exog_train = exog.loc["2012Q2":"2018Q4", covariables]

    target_test = target.loc["2019Q1":]
    exog_test = exog.loc["2019Q1":, covariables]

    ## Define y entrena modelo
    model = SARIMAX(target_train, exog=exog_train, order=(1, 0, 2), enforce_stationarity=False, enforce_invertibility=False)
    model_fit = model.fit(disp=False)

    # Forecast future steps
    predictions = model_fit.forecast(steps=len(target_test), exog=exog_test)


    # Reune resultados
    pronostico = pd.DataFrame( [ 
                    [
                        #str(predictions.index[-1]).split()[0],
                        predictions.index[-1],
                        modelos_nombres[modelo], 
                        np.exp(predictions.iloc[-1])*ive_nivel] 
                ], 
                    columns=["Date", "Modelo", "prediccion_nivel"]
    )

    return pronostico

def get_SHAP(
    target : pd.DataFrame, 
    exog : pd.DataFrame,
    modelo : str, 
    covariables : List[str], 
    ) -> pd.DataFrame:

    ## Define conjunto de entrenamiento y prueba
    target_train = target.loc["2012Q2":"2018Q4"].reset_index(drop=True)
    exog_train = exog.loc["2012Q2":"2018Q4", covariables].reset_index(drop=True)

    target_test = target.loc["2019Q1":].reset_index(drop=True)
    exog_test = exog.loc["2019Q1":, covariables].reset_index(drop=True)

    ## Define y entrena modelo
    model = SARIMAX(target_train, exog=exog_train, order=(1, 0, 2), enforce_stationarity=False, enforce_invertibility=False)
    model_fit = model.fit(disp=False)

    # Forecast future steps
    predictions = model_fit.forecast(steps=len(target_test), exog=exog_test)

    # Definimos la función de predicción para que el KernelExplainer la entienda
    def predict_func(model_fit, data):
        # En ARIMAX puedes usar forecast o get_prediction para generar las predicciones
        return model_fit.forecast(steps=len(data), exog=data)

    # Configurar el Kernel Explainer utilizando un subconjunto de datos como fondo
    #explainer = shap.KernelExplainer(lambda x: predict_func(model_fit, x), exog_test)
    print(f"Calculando SHAP Values para el Modelo {modelo}")
    explainer = shap.Explainer(lambda x: predict_func(model_fit, x), exog_test)


    # Calcular los valores SHAP para tus datos de interés
    #shap_values = explainer.shap_values(exog_test)
    explainer_values = explainer(exog_test)

    base_value = explainer_values.base_values[-1]*100
    shap_values = explainer_values.values[-1]*100

    # Reúne resultados
    df_SHAP = pd.DataFrame(
        {   
            #"Date" : [target.index[-1]]* (len(covariables) + 1), 
            "Modelo" : [modelos_nombres[modelo]] * (len(covariables) + 1), 
            "Variable" : ["Base"] + covariables, 
            "Contribución" : [base_value] + list(shap_values)
        }
    )

    df_SHAP["Variable"] = df_SHAP["Variable"].replace(long_name_covariables)

    return df_SHAP
    

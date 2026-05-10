## Cargamos rutina SARIMAX
from statsmodels.tsa.statespace.sarimax import SARIMAX
from typing import List 
import pandas as pd 
import numpy as np 

## Diccionarios con nombres completos de modelos
modelos_nombres = {f"M{i}" : f"Modelo lineal {i}"  for i in range(1,6)}

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
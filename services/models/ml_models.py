import tomllib
from pathlib import Path
import polars as pl
import pandas as pd
import numpy as np 
import statsmodels.tsa.x13 as x13
import polars.selectors as cs
import os

## Cargamos métodos que construyen las configuraciones generales y del storage
from utils import build_general_config, build_storage_config

## Importamos funciones para el cálculo de los errores
from sklearn.metrics import mean_squared_error, mean_absolute_error, root_mean_squared_error

## Load Machine Learning Models
from xgboost import XGBRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNetCV
from sklearn.linear_model import LassoCV
from sklearn.linear_model import RidgeCV
from sklearn.tree import DecisionTreeRegressor

from sklearn.preprocessing import StandardScaler

## Generamos función que calcula los errores promedio para cada modelo dado periodo
from scipy import stats
from scipy.stats import randint as sp_randint

# Tuning the hyper-parameters with RandomizedSearchCV
from sklearn.model_selection import RandomizedSearchCV

## GS packages
import gspread
from google.oauth2.service_account import Credentials

## Disable Warnings
import warnings
warnings.filterwarnings("ignore")

## Carga rich
from rich.console import Console
console = Console()

## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()

# 1. Authenticate
console.print("1.-", "Autenticando en GS", style="bold red")

GS_API_KEY_FILE = os.getenv("GS_API_KEY_FILE")

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(f'config/api_keys/{GS_API_KEY_FILE}', scopes=scopes)
client = gspread.authorize(creds)

# 3. Open Google Sheet and update
SPREADSHEET = os.getenv("GS_SPREADSHEET")
sh = client.open(SPREADSHEET)

# Diccionario de tabs de Google Sheet
sheets = [
            "pronosticos-modelos-ml", 
            "nivel-historico-pronostico-modelos-ml", 
            "tc-interanual-historico-pronostico-modelos-ml"
        ]

worksheets = {sheet : sh.worksheet(sheet) for sheet in sheets}


## Lista de Covariables
covariables = [ 'consumo_elect_al_publico', 'consumo_elect_comercio', 'consumo_elect_industria',
                'consumo_elect_total', 'consumo_elect_especiales', 'consumo_elect_residencial', 
                'evi_gee', 'ndbi_gee', 'ndvi_gee', 'precip', 'remesas_usd_trim', 'temp_air', 'temp_ls', 'viirs_bm_sum', 
                'gdp_us_const_trim', 'import_usd_cif', 'export_usd_fob']

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

## Definimos Train, Test y último valor disponible del IVE en niveles
target = data_set_cov[respuesta]
exog = data_set_cov[covariables]
ive_nivel = datos["indice_vol_encad"].to_numpy()[-2]

## Define conjunto de entrenamiento y prueba
y_train = target.loc["2012Q2":"2018Q4"]
X_train = exog.loc["2012Q2":"2018Q4", covariables]

trimestre_previo_a_pronosticar = target.index[-2]
trimestre_a_pronosticar = target.index[-1]

y_test = target.loc["2019Q1":trimestre_previo_a_pronosticar]
X_test = exog.loc["2019Q1":trimestre_previo_a_pronosticar, covariables]

print("""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
TRAINING {}\nTuning the hyper-parameters with RandomizedSearchCV
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n
""".format("XGBOOST"))
"""
parameters = {'max_depth': np.arange(2, 5, step=1),
              'learning_rate': 2**np.arange(-8., 2., step=2),
              'colsample_bytree': [0.6, 0.7, 0.8],
              'reg_alpha': [0.01, 0.1, 1],
              'reg_lambda': [0.01, 0.1, 1e-1, 1],
              "n_estimators" : [1,200]}
"""

parameters = {
              "loss" : ["linear", "square", "exponential"],
              "learning_rate": 2**np.arange(-8., 2., step=2),
              "n_estimators" : [1,200]
            }

xgb = XGBRegressor(objective='reg:pseudohubererror', random_state=0)
param_tuner_xgb = RandomizedSearchCV(xgb, parameters, n_iter=20, cv=5, refit=True, verbose=1)
param_tuner_xgb.fit(X_train, y_train)



print("""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
TRAINING {}\nTuning the hyper-parameters with RandomizedSearchCV
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n
""".format("AdaBoost"))

parameters = {
              "loss" : ["linear", "square", "exponential"],
              "learning_rate": 2**np.arange(-8., 2., step=2),
              "n_estimators" : [1,200]
            }

ada = AdaBoostRegressor(random_state=0)
param_tuner_ada = RandomizedSearchCV(ada, parameters, n_iter=20, cv=5, refit=True, verbose=1)
param_tuner_ada.fit(X_train, y_train)


print("""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
TRAINING {}\nTuning the hyper-parameters with RandomizedSearchCV
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n
""".format("Random Forest"))

# build a classifier
clf = RandomForestRegressor(random_state=0)

# specify parameters and distributions to sample from
param_dist = {"max_depth": [3, None],
              "max_features": sp_randint(1, 11),
              "min_samples_leaf": sp_randint(1, 11),
              "bootstrap": [True, False],
              "criterion": ["friedman_mse", "squared_error"],
              "n_estimators" : [1,200]}

# run randomized search
n_iter_search = 20
param_tuner_rf = RandomizedSearchCV(clf, param_distributions=param_dist, n_iter=n_iter_search, cv=5, refit=True)

param_tuner_rf.fit(X_train, y_train)

print("""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
TRAINING {}\nTuning the hyper-parameters with RandomizedSearchCV
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n
""".format("Elastic Net"))


elastic_net_regr = ElasticNetCV(l1_ratio = 0.5,cv=5, random_state=0)
elastic_net_regr.fit(X_train, y_train)


print("""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
TRAINING {}\nTuning the hyper-parameters with RandomizedSearchCV
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n
""".format("Lasso"))

lasso_regr = LassoCV(cv=5, random_state=0)
lasso_regr.fit(X_train, y_train)


print("""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
TRAINING {}\nTuning the hyper-parameters with RandomizedSearchCV
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n
""".format("Ridge"))

ridge_regr = RidgeCV(cv=5)
ridge_regr.fit(X_train, y_train)


print("""
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
TRAINING {}\nTuning the hyper-parameters with RandomizedSearchCV
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n
""".format("Decision Tree"))


# build model
decision_tree_model = DecisionTreeRegressor(random_state=0)

# specify parameters and distributions to sample from
param_dist = {"max_depth": [3, None],
              "max_features": sp_randint(1, 11),
              "min_samples_leaf": sp_randint(1, 11),
              "criterion": ["friedman_mse", "squared_error"],
              "splitter" : ["best", "random"]}

# run randomized search
n_iter_search = 20
param_tuner_dt = RandomizedSearchCV(decision_tree_model, param_distributions=param_dist, n_iter=n_iter_search, cv=5, refit=True)

param_tuner_dt.fit(X_train, y_train)

## Definimos función que calcula los errores dado un modelo

def compute_errors(model, model_name):
    ypred_trn = model.predict(X_train)
    ypred_tst = model.predict(X_test)

    mse_train, mse_test = mean_squared_error(y_train, ypred_trn), mean_squared_error(y_test, ypred_tst)
    mae_train, mae_test = mean_absolute_error(y_train, ypred_trn), mean_absolute_error(y_test, ypred_tst)
    rmse_train, rmse_test = root_mean_squared_error(y_train, ypred_trn), mean_absolute_error(y_test, ypred_tst)

    print('Train MSE = {:.6f}, Test MSE = {:.6f}\n' \
          'Train MAE = {:.6f}, Test MAE = {:.6f}\n'\
          'Train RMSE = {:.6f}, Test RMSE = {:.6f}'.format(mse_train, mse_test, mae_train, mae_test, rmse_train, rmse_test))

    data = [(model_name, "Training", mse_train, mae_train, rmse_train),
            (model_name, "Test", mse_test, mae_test, rmse_test)]

    return pd.DataFrame(data, columns=["Modelo", "Datos", "MSE", "MAE", "RMSE"])

### Resumen
resumen = pd.concat([
    compute_errors(param_tuner_xgb.best_estimator_, "XGBoost"),
    compute_errors(param_tuner_rf.best_estimator_, "Random Forest"),
    compute_errors(elastic_net_regr, "Elastic Net"),
    compute_errors(elastic_net_regr, "Lasso"),
    #compute_errors(ridge_regr, "Ridge"),
    compute_errors(param_tuner_dt, "Decision Tree Regresor"),
    compute_errors(param_tuner_ada.best_estimator_, "AdaBoost")
], ignore_index=True)

rmse_modelos = dict(
            resumen.query("Datos=='Test'")[["Modelo", "RMSE"]].to_records(index = False)
        )


## Creamos diccionario de modelos
modelos = {
    "XGBoost" : param_tuner_xgb.best_estimator_,
    "AdaBoost" : param_tuner_ada.best_estimator_,
    "Random Forest" : param_tuner_rf.best_estimator_,
    "Elastic Net" : elastic_net_regr,
    "Lasso" : elastic_net_regr,
    #"Ridge" : ridge_regr,
    "Decision Tree Regresor" : param_tuner_dt
}

X_forecast = exog.loc[[exog.index[-1]], covariables]

pronosticos_ml = []

for modelo_name, modelo in modelos.items():
    rmse = rmse_modelos[modelo_name]
    pronostico = modelo.predict(X_forecast)[0]
    pronostico_nivel = np.exp(pronostico)*ive_nivel

    pronosticos_ml.append(
        [
            trimestre_a_pronosticar, 
            modelo_name, 
            rmse, 
            pronostico,
            pronostico_nivel
        ]
    )

####----------------------------------------------- ####
# pronosticos-modelos-ml
####----------------------------------------------- ####

pronosticos_ml = pd.DataFrame(
    pronosticos_ml, 
    columns = ["Date", "Modelo", "rmse", "prediccion_tc_trimestral", "prediccion_nivel"]
)

## Agregamos valor del IVE del trimestre anterior
pronosticos_ml["trimestre_anual_anterior"] = datos.to_pandas()["indice_vol_encad"].iloc[-5]

## Calcula crecimiento interanual
predicciones_modelos = pl.from_pandas(pronosticos_ml)

predicciones_modelos = predicciones_modelos.with_columns(
    ### Calculamos crecimiento interanual
    prediccion_tc_interanual = 
    (
        (
            pl.col("prediccion_nivel")/pl.col("trimestre_anual_anterior")
        ) -1 
    ), 
).with_columns(
    pl.col("Date").cast(pl.Datetime("us"))
).select("Date", "Modelo", "rmse", "prediccion_tc_trimestral", "prediccion_tc_interanual", "prediccion_nivel")

####----------------------------------------------- ####
####      nivel-historico-pronostico-modelos-ml
####----------------------------------------------- ####

# Cargamos originales
ive = pl.read_delta(
        f"s3://{config['BUCKET_NAME']}/{respuesta}",
        storage_options=storage_options,
    )

## Construimos dataframe

def crea_data_frame(
    ive_data : pl.DataFrame,
    ive_var : str,
    modelo : str
    ) -> pl.DataFrame:
    
    datos = pl.concat(
                                        [   
                                            ## Agregamos valor histórico del IVE
                                            ive_data.rename({"datetime" : "Date"}), 
                                            ## Agregamos media del pronóstico del IVE en nivel para los 5 Modelos
                                            predicciones_modelos.filter(Modelo=modelo).select("Date", ive_var), 
                                            ## Agregamos limite inferior del pronóstico del IVE
                                            predicciones_modelos.filter(Modelo=modelo).select("Date", ive_var).rename({ive_var : "lim_inf_prediccion_nivel"}), 
                                            ## Agregamos limite superior del pronóstico del IVE
                                            predicciones_modelos.filter(Modelo=modelo).select("Date", ive_var).rename({ive_var : "lim_sup_prediccion_nivel"}),                                          
                                        ], how = "align"
                                ).to_pandas()
    datos["Modelo"] = modelo
    columnas = ["Date", "Modelo", "indice_vol_encad", ive_var, "lim_inf_prediccion_nivel", "lim_sup_prediccion_nivel"]

    datos = datos[columnas]

    ## Imputamos el valor histórico del último trimestre observado a todas las columnas numericas
    datos.iloc[-2, 3:] = datos.iloc[-2, 2]
    datos = pl.from_pandas(datos)
    datos = datos.rename(
        {
            "indice_vol_encad" : "Histórico", 
            ive_var : "Pronóstico", 
            "lim_inf_prediccion_nivel" : "Límite inferior",
            "lim_sup_prediccion_nivel" : "Límite superior"
        }
    )

    return datos

nivel_historico_pronostico_modelos_ml = pl.concat([crea_data_frame(ive, "prediccion_nivel", modelo) for modelo in predicciones_modelos["Modelo"]])

####----------------------------------------------- ####
####      tc-interanual-historico-pronostico-modelos-ml
####----------------------------------------------- ####

# Construimos serie de crecimiento interanual original
ive_interanual = ive.with_columns((pl.col("indice_vol_encad")/pl.col("indice_vol_encad").shift(4))-1)

tc_interanual_historico_pronostico_modelos_ml = pl.concat([crea_data_frame(ive_interanual, "prediccion_tc_interanual", modelo) for modelo in predicciones_modelos["Modelo"]])


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
         cs.float().round(4)
        ).to_pandas().replace(np.nan, "")

### Reune tablas en un diccionario
outputs_tables = {
    "pronosticos-modelos-ml" : ajusta_df(predicciones_modelos), 
    "nivel-historico-pronostico-modelos-ml" : ajusta_df(nivel_historico_pronostico_modelos_ml), 
    "tc-interanual-historico-pronostico-modelos-ml" : ajusta_df(tc_interanual_historico_pronostico_modelos_ml)
}

#### Exportamos tablas a GS
console.print("5.-", "Exportamos Tablas a GS", style="bold red")

for sheet_name, worksheet in worksheets.items():
    # Upload data (headers + values)
    worksheet.update(
        [outputs_tables[sheet_name].columns.values.tolist()] + outputs_tables[sheet_name].values.tolist()
    )

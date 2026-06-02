import polars as pl 
from polars import Datetime, Float64
import streamlit as st
from typing import Dict

from deltalake import DeltaTable

from streamlit_echarts import st_pyecharts
import pyecharts.options as opts
from pyecharts.charts import Line
import pandas as pd 

import time 

import os 
import socket

## Función de construye el AWS_ENDPOINT_URL a partir del DNS del servidor y el puerto
def build_aws_endpoint_url() -> str :

    IP_DNS = socket.gethostbyname(os.getenv("RUSTFS_DNS"))
    PORT = os.getenv("RUSTFS_PORT")
    return f'http://{IP_DNS}:{PORT}'

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
        'AWS_ENDPOINT_URL': build_aws_endpoint_url(),
        'AWS_REGION': os.getenv("AWS_REGION"),
        'AWS_ACCESS_KEY_ID': os.getenv("AWS_ACCESS_KEY_ID"),
        'AWS_SECRET_ACCESS_KEY': os.getenv("AWS_SECRET_ACCESS_KEY"),
        'allow_http': os.getenv("allow_http")
    }

## Diccionario de nombres de archivos raw del Banco de la República 
BR_VAR_NAME : Dict[str,str]= {
    "indice_vol_encad" : "Producto Interno Bruto trimestral por el enfoque de la producción", 
    "remesas_usd_trim" : "Ingresos mensuales de remesas familiares",
    "export_usd_fob" : "Exportaciones",
    "import_usd_cif" : "Importaciones",
    "gdp_us_corriente" : "Producto Interno Bruto trimestral por el enfoque de la producción"
}

## Funcion que carga las tablas del almacenamiento de objetos
def load_delta_table(
    covariable : str,
    config : Dict[str,str],
    storage_options : Dict[str,str]
    ) -> pl.DataFrame:

    ## Construimos ruta de la tabla en el almacenamiento de objetos
    URL_DELTA_TABLE = f"s3://{config['BUCKET_NAME']}/{covariable}"

    ## Test si la tabla existe
    if DeltaTable.is_deltatable(URL_DELTA_TABLE, storage_options=storage_options):
        ## La tabla existe, cargamos los datos
        return pl.read_delta(
        URL_DELTA_TABLE,
        storage_options=storage_options,
        )

    else:
        ## Regregamos tabla vacía con el schema especifico
        return pl.DataFrame([], 
                    {
                        "datetime" : Datetime(time_unit='us', time_zone=None) , 
                        covariable : Float64}
                    )



## Función que crea la gráfica de serie de tiempo
def time_series_plot(ts_var : str, 
                     metadata : Dict[str, str], 
                     config : Dict[str,str], 
                     storage_config : Dict[str,str]
    ) -> None:
    
    st.title(metadata["descripcion"])

    ## Cargamos los datos de Delta Lake al llamar a la función
    data = load_delta_table(ts_var, config, storage_config)

    if not data.is_empty():
        data2plot = data.with_columns(
            pl.col(ts_var).round(3),
            pl.col("datetime").dt.year().cast(pl.Utf8) + "Q" + pl.col("datetime").dt.quarter().cast(pl.Utf8) # Ajustamos el trimestre
            ).to_numpy()

        linea = (
            Line()
            .add_xaxis(xaxis_data=[item[0] for item in data2plot])
            .add_yaxis(
                series_name="",
                y_axis=[item[1] for item in data2plot],
                yaxis_index=0,
                #is_smooth=True,
                is_symbol_show=False,
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=metadata["variable"]),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),

                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name_location="start",
                    min_=round(data.select(ts_var).min().item(), 2),
                    max_=round(data.select(ts_var).max().item(), 2) ,
                    is_scale=True,
                    axistick_opts=opts.AxisTickOpts(is_inside=False),
                ),
            )
        )

        
        st_pyecharts(linea)
    else:
        st.warning('La Tabla no está disponible', icon="⚠️")

    st.markdown(
        f"""
        * **Frecuencia** : {metadata['frecuencia_actualizacion']} 
        * **Frecuencia de Actualización** : {metadata['frecuencia_actualizacion_delta']}
        * **Rezago** : {metadata['rezago_fecha_actual']}
        * **Fuente** : {metadata['fuente']}
        """
    )

## Función que crea la gráfica de serie de tiempo y tiene boton de carga de archivo
def time_series_plot(ts_var : str, 
                     metadata : Dict[str, str], 
                     config : Dict[str,str], 
                     storage_config : Dict[str,str]
    ) -> None:
    
    st.title(metadata["descripcion"])

    ## Cargamos los datos de Delta Lake al llamar a la función
    data = load_delta_table(ts_var, config, storage_config)

    if not data.is_empty():
        data2plot = data.with_columns(
            pl.col(ts_var).round(3),
            pl.col("datetime").dt.year().cast(pl.Utf8) + "Q" + pl.col("datetime").dt.quarter().cast(pl.Utf8) # Ajustamos el trimestre
            ).to_numpy()

        linea = (
            Line()
            .add_xaxis(xaxis_data=[item[0] for item in data2plot])
            .add_yaxis(
                series_name="",
                y_axis=[item[1] for item in data2plot],
                yaxis_index=0,
                #is_smooth=True,
                is_symbol_show=False,
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=metadata["variable"]),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),

                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name_location="start",
                    min_=round(data.select(ts_var).min().item(), 2),
                    max_=round(data.select(ts_var).max().item(), 2) ,
                    is_scale=True,
                    axistick_opts=opts.AxisTickOpts(is_inside=False),
                ),
            )
        )

        
        st_pyecharts(linea)
    else:
        st.warning('La Tabla no está disponible', icon="⚠️")

    st.markdown(
        f"""
        * **Frecuencia** : {metadata['frecuencia_actualizacion']} 
        * **Frecuencia de Actualización** : {metadata['frecuencia_actualizacion_delta']}
        * **Rezago** : {metadata['rezago_fecha_actual']}
        * **Fuente** : {metadata['fuente']}
        """
    )

    if ts_var in ["consumo_elect_total", "export_usd_fob", "import_usd_cif", "indice_vol_encad", "remesas_usd_trim", "gdp_us_corriente"]:
        
        if "upload_key" not in st.session_state:
            st.session_state["upload_key"] = 0

        #def reset_uploader():
        #    st.session_state["upload_key"] += 1


        uploaded_file = st.file_uploader("**Sube los datos**", key=st.session_state["upload_key"], type=["csv", "xlsx"])

        if uploaded_file !=None:
            ### Cargamos y guardamos en Delta Lake el archivo suministrado por el usuario
            if ts_var in ["consumo_elect_total"]:
                transforma_and_load_electricidad(ts_var, uploaded_file, config, storage_config)
            else:
                transforma_and_load_bc(ts_var, uploaded_file, config, storage_config)
            #st.button("Reset", on_click=reset_uploader)
            st.session_state["upload_key"] += 1
            #st.success('Se limpio caché', icon="✅")
            ### Booteamos la aplicación para cargar los datos recientemente actualizados
            st.rerun()

### Función que transforma los datos crudos del Banco Central para su posterior carga en Delta Lake 
def transforma_and_load_bc( ts_var : str,
                            uploaded_file, 
                            config : Dict[str,str], 
                            storage_config : Dict[str,str]
    ) -> None:

    ## Cargamos datos
    raw_data = pd.read_csv(uploaded_file, skiprows = 3)
    
    ## Eliminamos último registro
    raw_data = raw_data.iloc[:-1]
    
    ## Transformamos tabla a formato short
    raw_data = raw_data.set_index("Concepto").T.reset_index()

    ## Removemos caracter '(p)' del indice de tiempo
    raw_data["index"] = raw_data["index"].str.replace("(p)", "").str.replace("(e)", "").str.replace("(r)", "")

    ## Transformamos el DataFrame a polars DataFrame
    raw_data = pl.from_pandas(raw_data) 

    ## Creamos variale de tiempo
    raw_data = raw_data.with_columns(
        pl.col("index").str.split_exact("-", 1).alias("fields")
    ).unnest("fields")

    raw_data = raw_data.with_columns(
        pl.col("field_1").cast(pl.Int8).map_elements(lambda x : f"{x:02d}")
    )

    ## Modificamos los valores de meses para el IVE
    if ts_var in ["indice_vol_encad", "gdp_us_corriente"] :
        raw_data = raw_data.with_columns(
            pl.col("field_1").str.replace_many(
                {
                    "02" : "04",
                    "03" : "07", 
                    "04" : "11",
                }
            )
        )

    ## Creamos datetime en string
    raw_data = raw_data.with_columns(
        datetime = pl.concat_str(
            [
                pl.col("field_0"), pl.col("field_1"), pl.lit("01")
            ], 
            separator = "-"
        )
    )

    ## Convertimos datetime a DateTime
    raw_data = raw_data.with_columns(
        pl.col("datetime").str.to_datetime("%Y-%m-%d")
    )

    ## Seleccionamos las columnas nesarias
    raw_data = raw_data.select(
        "datetime", BR_VAR_NAME[ts_var]
    ).rename(
        {
            BR_VAR_NAME[ts_var]: ts_var
        }
    )
    
    ### Agregamos los datos a trimestre
    datos_q = raw_data.group_by_dynamic("datetime", every="1q", closed="left").agg(pl.sum(ts_var))

    ### Guardamos datos en formato Delta Table en RustFS
    datos_q.write_delta(
        f"s3://{config['BUCKET_NAME']}/{ts_var}",
        storage_options=storage_config,
        mode = "overwrite"
    )

    ### Mensaje de acción exitosa
    st.success('La tabla se actualizó exitosamente', icon="✅")

    time.sleep(1)

### Función que transforma los datos crudos del Banco Central para su posterior carga en Delta Lake 
def transforma_and_load_electricidad( ts_var : str,
                            uploaded_file, 
                            config : Dict[str,str], 
                            storage_config : Dict[str,str]
    ) -> None:


    df = pd.read_excel(uploaded_file, sheet_name="RESUMEN FINAL", header = 1 )
    df =df.dropna(subset=["CLASIFICACIÓN"])

    df["AÑO"] = df["AÑO"].ffill()
    df["AÑO"] = df["AÑO"].astype(str).str.replace("**","")

    df["CLASIFICACIÓN"] = df["CLASIFICACIÓN"].str.replace("*","")
    df = df.dropna(subset=["AÑO", "CLASIFICACIÓN"]).set_index(["AÑO", "CLASIFICACIÓN"]).reset_index()
    df = df.drop(columns="TOTAL")
    df["AÑO"] = df["AÑO"].astype(int)

    df = df.query("AÑO >= 2012")
    mapping = {
        'ENE': '01',
        'FEB': '02',
        'MAR': '03',
        'ABR': '04',
        'MAY': '05',
        'JUN': '06',
        'JUL': '07',
        'AGO': '08',
        'SEP': '09',
        'OCT': '10',
        'NOV': '11',
        'DIC': '12'
    }
    
    df = df.rename(columns = mapping).melt(id_vars=["AÑO", "CLASIFICACIÓN"])
    df["AÑO"] = df["AÑO"].astype(str)
    df["datetime"] = df["AÑO"] + "-" +df["variable"] + "-01"
    df = df[["datetime", "CLASIFICACIÓN", "value"]].pivot(index = "datetime", columns = "CLASIFICACIÓN", values = "value").reset_index()
    df = df.dropna()

    mapp_categorias = {
    'AL. PÚBLICO': 'consumo_elect_al_publico',
    'COMERCIO': 'consumo_elect_comercio',
    'ESPECIALES': 'consumo_elect_especiales',
    'INDUSTRIA': 'consumo_elect_industria',
    'RESIDENCIAL': 'consumo_elect_residencial'
    }

    df = df.rename(columns = mapp_categorias)
    df["consumo_elect_total"] = df[mapp_categorias.values()].sum(axis = 1)


    df = pl.from_pandas(df)
    df = df.with_columns(
    pl.col("datetime").str.to_datetime("%Y-%m-%d")
    )
    
    ### Agregamos los datos a trimestre
    covariables = list(mapp_categorias.values()) + ["consumo_elect_total"]

    datos_q = df.group_by_dynamic("datetime", every="1q", closed="left").agg(pl.sum(covariables))

    ### Guardamos datos en formato Delta Table en RustFS

    for covariable in covariables:
        datos_q.select("datetime", covariable).write_delta(
            f"s3://{config['BUCKET_NAME']}/{covariable}",
            storage_options=storage_config,
            mode = "overwrite"
        )

    ### Mensaje de acción exitosa
    st.success('La tabla se actualizó exitosamente', icon="✅")

    time.sleep(1)

#############################################
### ------------ SUBNACIONAL -------------- #
#############################################

departamento_to_gid = {'Ahuachapán': 'SLV_1',
 'Cabañas': 'SLV_2',
 'Chalatenango': 'SLV_3',
 'Cuscatlán': 'SLV_4',
 'La Libertad': 'SLV_5',
 'La Paz': 'SLV_6',
 'La Unión': 'SLV_7',
 'Morazán': 'SLV_8',
 'San Miguel': 'SLV_9',
 'San Salvador': 'SLV_10',
 'San Vicente': 'SLV_11',
 'Santa Ana': 'SLV_12',
 'Sonsonate': 'SLV_13',
 'Usulután': 'SLV_14'}

departamentos_lista = list(departamento_to_gid.keys())

## Función que crea la gráfica de serie de tiempo y tiene boton de carga de archivo para el componente subnacional
def time_series_plot_subnacional(ts_var : str, 
                     metadata : Dict[str, str], 
                     config : Dict[str,str], 
                     storage_config : Dict[str,str]
    ) -> None:
    
    st.title(metadata["descripcion"])

    ## Cargamos los datos de Delta Lake al llamar a la función
    data = load_delta_table(ts_var, config, storage_config)

    if not data.is_empty():

        option = st.selectbox(
            "Selecciona el Departamento",
            departamentos_lista,
            index=0,
            placeholder="Departamento",
        )

        st.markdown(f"## Departamento {option}" )

        data_depto = data.filter(
            (pl.col("GID_1") == departamento_to_gid[option]) &
            (pl.col("datetime") >= pl.datetime(2012,1,1))
        ).drop("GID_1")
        data2plot = data_depto.with_columns(
            pl.col(ts_var).round(3),
            pl.col("datetime").dt.year().cast(pl.Utf8) + "Q" + pl.col("datetime").dt.quarter().cast(pl.Utf8) # Ajustamos el trimestre
            ).to_numpy()

        linea = (
            Line()
            .add_xaxis(xaxis_data=[item[0] for item in data2plot])
            .add_yaxis(
                series_name="",
                y_axis=[item[1] for item in data2plot],
                yaxis_index=0,
                #is_smooth=True,
                is_symbol_show=False,
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=metadata["variable"]),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),

                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name_location="start",
                    min_=round(data_depto.select(ts_var).min().item(), 2),
                    max_=round(data_depto.select(ts_var).max().item(), 2) ,
                    is_scale=True,
                    axistick_opts=opts.AxisTickOpts(is_inside=False),
                ),
            )
        )

        
        st_pyecharts(linea)
    else:
        st.warning('La Tabla no está disponible', icon="⚠️")

    st.markdown(
        f"""
        * **Frecuencia** : {metadata['frecuencia_actualizacion']} 
        * **Frecuencia de Actualización** : {metadata['frecuencia_actualizacion_delta']}
        * **Rezago** : {metadata['rezago_fecha_actual']}
        * **Fuente** : {metadata['fuente']}
        """
    )

    if ts_var in ["electricidad_departamento", "gdp_us_corriente"]:
        st.warning('Aquí se agregará método para cargar la tabla', icon="⚠️")

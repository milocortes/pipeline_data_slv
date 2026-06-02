import streamlit as st
from jinja2 import Template
import os 

## Paquetes para desencadenar la DAG con Airflow REST API
import requests
from datetime import datetime

## Rutina para evaluar si se tienen todas las covariables disponibles
from models import get_available_cov_ml

## Carga variables de entorno 
AIRFLOW_APISERVER_DOMAIN = os.getenv("AIRFLOW_APISERVER_DOMAIN")
AIRFLOW_APISERVER_PORT = os.getenv("AIRFLOW_APISERVER_PORT")
_AIRFLOW_WWW_USER_PASSWORD = os.getenv("_AIRFLOW_WWW_USER_PASSWORD")
_AIRFLOW_WWW_USER_USERNAME = os.getenv("_AIRFLOW_WWW_USER_USERNAME")

st.title("Pronostico Modelos de Aprendizaje de Máquina")

test_disponibilidad = get_available_cov_ml()

# 1. Define your Markdown template with Jinja2 placeholders
template_disponibilidad = """

:red-badge[⚠️ El pronóstico del IVE para el trimestre **NO** puede realizarse].

**No se encuentra disponible el dato del trimestre a pronosticar para las siguientes variables**:

{% for cov in covariables %}
  * {{ cov }}
{% endfor %}
"""

if test_disponibilidad:

    # 2. Render the template with dynamic data
    template = Template(template_disponibilidad)
    rendered_markdown = template.render(covariables = test_disponibilidad)

    # 3. Display in Streamlit
    st.markdown(rendered_markdown)

else:
    if st.button("Pronóstico IVE Modelos de Aprendizaje de Máquina"):

        ## Esta información debe ir en un archivo de configuración. Por el momento quedará hardcodeado
        url = f"{AIRFLOW_APISERVER_DOMAIN}:{AIRFLOW_APISERVER_PORT}/api/v2/dags/forecast_modelos_ml/dagRuns"
        url_token = f"{AIRFLOW_APISERVER_DOMAIN}:{AIRFLOW_APISERVER_PORT}/auth/token"

        headers_token = {
            "Content-Type" : "application/json"
        }

        data_token = {
            "username": _AIRFLOW_WWW_USER_USERNAME,
            "password": _AIRFLOW_WWW_USER_PASSWORD
        }

        response_token = requests.post(url_token, headers=headers_token, json=data_token)

        token = response_token.json()["access_token"]

        with st.spinner("Wait for it...", show_time=True):
            headers = {
                "Authorization" : f"Bearer {token}",
                "Content-Type" : "application/json"
            }

            data = {
                "logical_date" : datetime.now().astimezone().isoformat()#datetime.now().isoformat()
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                st.success("DAG Triggered Successfully")
            else:
                st.error(f"Failed: {response.text}")


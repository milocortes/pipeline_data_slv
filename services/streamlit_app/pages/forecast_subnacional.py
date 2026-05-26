import streamlit as st
from jinja2 import Template

## Paquetes para desencadenar la DAG con Airflow REST API
import requests
from datetime import datetime

## Rutina para evaluar si se tienen todas las covariables disponibles
from models import get_available_cov_ml

st.title("Estimación PIB Subnacional con Modelo Panel Dinámico Bayesiano")

test_disponibilidad = get_available_cov_ml()

# 1. Define your Markdown template with Jinja2 placeholders
template_disponibilidad = """

:red-badge[⚠️ La estimación del PIB Subnacional **NO** puede realizarse].

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
    if st.button("Estimación PIB Subnacional"):

        ## Esta información debe ir en un archivo de configuración. Por el momento quedará hardcodeado
        url = "http://localhost:8080/api/v2/dags/estimacion_subnacional/dagRuns"
        url_token = "http://localhost:8080/auth/token"

        headers_token = {
            "Content-Type" : "application/json"
        }

        data_token = {
            "username": "airflow",
            "password": "airflow"
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


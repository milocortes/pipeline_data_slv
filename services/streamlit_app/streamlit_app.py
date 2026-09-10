import streamlit as st

from backend.hub import Hub
from pages.pages import pages

st.set_page_config(
    page_title="Administración Backend",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

if 'hub' not in st.session_state:
  st.session_state.hub = Hub()

if 'logged_in' in st.session_state and st.session_state.logged_in:
  page = st.navigation([
    pages['home'], 
    pages["covariables"],
    pages["forecast_arimax"],
    pages["forecast_ml"],
    pages["subnacional_covariables"],
    pages["forecast_subnacional"],
    pages["actualiza_tokens"],
    pages["envia_respaldos"],
    pages["signup"],
    pages['logout']]
    )
else:
  page = st.navigation([pages['login']])

page.run()

with st.sidebar:
    st.markdown(
        ":material/code: [streamlit-echarts](https://github.com/andfanilo/streamlit-echarts)"
    )
    st.caption("Made in :streamlit: by [@milocortes](https://github.com/milocortes)")
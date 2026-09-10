import streamlit as st
from pages.icons import LOGIN, LOGOUT, SIGNUP, HOME

pages = {
  "login": st.Page("pages/login.py", title="Log in", icon=LOGIN),
  #"signup": st.Page("frontend/signup.py", title="Sign up", icon=SIGNUP),
  "home": st.Page("pages/home.py", title="Home", icon=HOME),
  "logout": st.Page("pages/logout.py", title="Log out", icon=LOGOUT), 
  "covariables" : st.Page("pages/covariables.py", title="Covariables", icon=":material/code:"),
  "forecast_arimax" : st.Page("pages/forecast_arimax.py", title = "Pronóstico Modelos Lineales", icon = "🚀"), 
  "forecast_ml" : st.Page("pages/forecast_ml.py", title = "Pronóstico Modelos Aprendizaje de Máquina", icon = "📊"), 
  "subnacional_covariables" : st.Page("pages/subnacional_covariables.py", title="Covariables Subnacional", icon=":material/code:"),
  "forecast_subnacional" : st.Page("pages/forecast_subnacional.py", title="Estimación Subnacional", icon="🌍"),
  "actualiza_tokens" : st.Page("pages/actualiza_tokens.py", title = "Actualización de Tokens", icon = "🔑"),
  "signup" : st.Page("pages/signup.py", title = "Agrega Usuario", icon = ":material/person_add:"),
  "envia_respaldos" : st.Page("pages/envia_respaldos.py", title = "Respaldo de Pronósticos", icon = ":material/security:")
}
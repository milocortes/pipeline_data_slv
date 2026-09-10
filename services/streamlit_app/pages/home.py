import streamlit as st

hub = st.session_state.hub
user = st.session_state.user

st.title(":material/bar_chart: Aplicación para el Pronóstico del IVE")
st.title(f"Welcome, {user.username}!")
st.markdown(
    """
    La aplicación gestiona el Backend de datos para el Pronóstico del IVE y está compuesta por las vistas de : 
    * Administración de Covariables.
    * Pronóstico de los modelos lineales ARIMAX.
    * Pronóstico de los modelos de Aprendizaje de Máquina. 
    """
)

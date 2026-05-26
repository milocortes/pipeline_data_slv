import streamlit as st

st.set_page_config(
    page_title="Administración Backend",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

pg = st.navigation(
    [
        st.Page(
            "pages/showcase.py",
            title="Home",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page("pages/covariables.py", title="Covariables", icon=":material/code:"),
        st.Page("pages/forecast_arimax.py", title = "Pronóstico Modelos Lineales", icon = "🚀"), 
        st.Page("pages/forecast_ml.py", title = "Pronóstico Modelos Aprendizaje de Máquina", icon = "📊"), 
        st.Page("pages/subnacional_covariables.py", title="Covariables Subnacional", icon=":material/code:"),
        st.Page("pages/forecast_subnacional.py", title="Estimación Subnacional", icon="🌍"),
        st.Page("pages/actualiza_tokens.py", title = "Actualización de Tokens", icon = "🔑"),

    ]
)
pg.run()

with st.sidebar:
    st.markdown(
        ":material/code: [streamlit-echarts](https://github.com/andfanilo/streamlit-echarts)"
    )
    st.caption("Made in :streamlit: by [@milocortes](https://github.com/milocortes)")
    #st.markdown(
    #    '<div style="margin-top: 0.75em;"><a href="https://www.buymeacoffee.com/andfanilo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174" style="border-radius: 12px;"></a></div>',
    #    unsafe_allow_html=True,
    #)
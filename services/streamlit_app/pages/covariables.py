import inspect
import textwrap

import streamlit as st

from cov_geoespaciales import RENDER_GEOESPACIAL
from cov_administrativas import RENDER_ADMINISTRATIVAS

from streamlit_echarts import st_pyecharts
from pyecharts.charts import Line

#st.title("Covariables")

with st.sidebar:
    st.header("Covariables")

    selected_category = st.selectbox(
        label="Categoría",
        options=["Geoespaciales", "Administrativas"] ,
        key="ex_category",
        bind="query-params",
    )

    series_by_category = (
        RENDER_GEOESPACIAL if selected_category == "Geoespaciales" else RENDER_ADMINISTRATIVAS
    )


    selected_serie = st.selectbox(
        label="Variable",
        options=list(series_by_category.keys()),
        key="ex_demo",
        bind="query-params",
    )

    plot_serie = series_by_category[selected_serie]

plot_serie()
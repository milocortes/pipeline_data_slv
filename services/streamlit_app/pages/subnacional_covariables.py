import inspect
import textwrap

import streamlit as st

from cov_subnacional import RENDER_SUBNACIONAL

from streamlit_echarts import st_pyecharts
from pyecharts.charts import Line

#st.title("Covariables")

with st.sidebar:
    st.header("Covariables Subnacional")

    series_by_category = RENDER_SUBNACIONAL


    selected_serie = st.selectbox(
        label="Variable",
        options=list(series_by_category.keys()),
        key="ex_demo",
        bind="query-params",
    )

    plot_serie = series_by_category[selected_serie]

plot_serie()
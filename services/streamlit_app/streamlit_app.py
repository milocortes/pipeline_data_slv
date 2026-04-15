import streamlit as st

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Dashboard",
    #page_icon="🌦️",
    # Make the content take up the width of the page:
    layout="wide",

)

pages = {
    "Covariables": [
        st.Page("covariables/gdp_us_const_trim.py", title="USA GDP"),
        st.Page("covariables/precip.py", title="Precipitación"),
    ],
    #"Table" : [
    #    st.Page("table.py", title = "Table"),
    #]
}

pg = st.navigation(pages, position="top")
pg.run()
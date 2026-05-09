import streamlit as st
from jinja2 import Template

from models import get_available_cov_arimax

st.title("Pronostico Modelos Lineales ARIMAX")

test_disponibilidad = get_available_cov_arimax()

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
    if st.button("Pronóstico IVE ARIMAX"):
        st.write("Button was pressed!")
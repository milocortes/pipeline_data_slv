import streamlit as st

# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False


st.title("Actualización de Tokens")
st.markdown(
    """
    ## Luces VIIRS Black Marble

    * Se requiere de la creación de una cuenta (email y contraseña) para acceder al conjunto de datos de NASA Earth Data. 
      Leer con detenimiento las instrucciones del repositorio del paquete blackmarbler en la siguiente [liga](https://worldbank.github.io/blackmarbler/)
    * Sigue los pasos para crear un token.

    :red-badge[⚠️ NOTA: los tokens tienen una vigencia de 2 meses].
    """
)


text_input = st.text_input(
        "Agrega tu nuevo Token de VIIRS Black Marble aquí 👇",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder="VIIRS Token",
    )


st.markdown(
    """
    ## GDP constante trimestral de EEUU

    """
)
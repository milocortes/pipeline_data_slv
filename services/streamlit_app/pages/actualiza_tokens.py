import streamlit as st
from utils import get_tokens, actualiza_token

# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

## Cargamos tokens actuales
#tokens = get_tokens()
#st.dataframe(tokens, use_container_width=True)


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

# Create a form container
with st.form(key="viirs_input_form"):
    new_token_viirs = st.text_input(
        "Agrega tu nuevo Token de VIIRS Black Marble aquí 👇",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder="VIIRS Token",
    )
    
    # Every form requires a submit button
    submitted_viirs = st.form_submit_button(label="Submit")

# Execute actions only after the submit button is clicked
if submitted_viirs:   
    actualiza_token("BLACKMARBLE", new_token_viirs)
    st.write(f"El nuevo token para VIIRS Black Marble es: :blue-badge[{new_token_viirs}]")


st.markdown(
    """
    ## GDP constante trimestral de EEUU

    Tenga en cuenta que no puede [solicitar ni ver sus claves de API](https://fredaccount.stlouisfed.org/login/secure/) sin antes iniciar sesión en su cuenta de usuario de [fredaccount.stlouisfed.org](https://fredaccount.stlouisfed.org/login/secure/).
    * Todas las solicitudes de servicios web requieren una clave de API para identificar las solicitudes.
    * Los desarrolladores deben solicitar una clave de API distinta para cada aplicación que desarrollen.
    * Todos los usuarios de una aplicación deberán utilizar su propia clave de API.

    La clave de API se establece mediante la variable `api_key`, una cadena alfanumérica de 32 caracteres en minúsculas.

    """
)

# Create a form container
with st.form(key="fred_input_form"):
    new_token_fred = st.text_input(
        "Agrega tu nuevo Token de Fred aquí 👇",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder="FRED Token",
    )
    
    # Every form requires a submit button
    submitted_fred = st.form_submit_button(label="Submit")

# Execute actions only after the submit button is clicked
if submitted_fred:   
    actualiza_token("FRED", new_token_fred)
    st.write(f"El nuevo token para FRED es: :blue-badge[{new_token_fred}]")


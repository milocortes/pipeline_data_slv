from .administrativas import render_gdp_us_const_trim
from .administrativas import render_indice_vol_encad
from .administrativas import (render_consumo_elect_total, 
                              render_consumo_elect_al_publico, 
                              render_consumo_elect_comercio, 
                              render_consumo_elect_especiales, 
                              render_consumo_elect_industria, 
                              render_consumo_elect_residencial,)
from .administrativas import render_export_usd_fob
from .administrativas import render_import_usd_cif
from .administrativas import render_remesas_usd_trim




RENDER_ADMINISTRATIVAS = {
    "GDP constante trimestral de EEUU"  : render_gdp_us_const_trim, 
    "Indice de Volumen Encadenado" : render_indice_vol_encad, 
    "Consumo Electrico Total" : render_consumo_elect_total, 
    "Consumo Electrico Al Público" : render_consumo_elect_al_publico, 
    "Consumo Electrico Comercio" : render_consumo_elect_comercio, 
    "Consumo Electrico Especiales" : render_consumo_elect_especiales, 
    "Consumo Electrico Industria" : render_consumo_elect_industria, 
    "Consumo Electrico Residencial" : render_consumo_elect_residencial, 
    "Exportaciones" : render_export_usd_fob, 
    "Importaciones" : render_import_usd_cif, 
    "Remesas" : render_remesas_usd_trim 
}

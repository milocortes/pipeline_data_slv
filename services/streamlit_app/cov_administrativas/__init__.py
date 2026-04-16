from .administrativas import render_gdp_us_const_trim
from .administrativas import render_indice_vol_encad
from .administrativas import render_consumo_elect_total
from .administrativas import render_export_usd_fob
from .administrativas import render_import_usd_cif
from .administrativas import render_remesas_usd_trim




RENDER_ADMINISTRATIVAS = {
    "GDP constante trimestral de EEUU"  : render_gdp_us_const_trim, 
    "Indice de Volumen Encadenado" : render_indice_vol_encad, 
    "Consumo Electrico Total" : render_consumo_elect_total, 
    "Exportaciones" : render_export_usd_fob, 
    "Importaciones" : render_import_usd_cif, 
    "Remesas" : render_remesas_usd_trim 
}

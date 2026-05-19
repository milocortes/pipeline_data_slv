from .subnacional import render_gdp_ppp_departamento
from .subnacional import render_electricidad_departamento
from .subnacional import render_viirs_bm_sum_departamento
from .subnacional import render_poblacion_departamento
from .subnacional import render_gdp_us_corriente


RENDER_SUBNACIONAL = {
    #"GDP per capita at purchasing power parity (PPP)"  : render_gdp_ppp_departamento, 
    #"Población" : render_poblacion_departamento, 
    "Consumo Electrico Total" : render_electricidad_departamento, 
    "Luces Nocturnas VIIRS" : render_viirs_bm_sum_departamento, 
    "Producto Interno Bruto Trimestral (PIB T). Producción y gasto a precios corrientes" : render_gdp_us_corriente, 
}

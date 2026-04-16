from .geoespaciales import render_evi_gee
from .geoespaciales import render_gdp_us_const_trim
from .geoespaciales import render_ndbi_gee
from .geoespaciales import render_ndvi_gee
from .geoespaciales import render_precip




RENDER_GEOESPACIAL = {
    "EVI"  : render_evi_gee, 
    #"USA GDP" : render_gdp_us_const_trim, 
    "NDBI" : render_ndbi_gee, 
    "NDVI" : render_ndvi_gee, 
    "Precipitación" : render_precip 
}



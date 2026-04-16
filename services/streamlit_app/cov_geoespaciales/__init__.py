from .geoespaciales import render_evi_gee
from .geoespaciales import render_ndbi_gee
from .geoespaciales import render_ndvi_gee
from .geoespaciales import render_precip
from .geoespaciales import render_temp_air
from .geoespaciales import render_temp_ls




RENDER_GEOESPACIAL = {
    "EVI"  : render_evi_gee, 
    "Temperatura Aire ERA5" : render_temp_air, 
    "Temperatura Superficie MODIS" : render_temp_ls, 
    "NDBI" : render_ndbi_gee, 
    "NDVI" : render_ndvi_gee, 
    "Precipitación" : render_precip 
}



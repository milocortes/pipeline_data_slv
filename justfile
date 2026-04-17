# Default recipe
default:
  just --list

# Run evi_gee task
evi_gee:
  cd services/fetch_load_data/ && uv run tasks/evi_gee.py

# Run gdp_us_const_trim task
gdp_us_const_trim:
  cd services/fetch_load_data/ && uv run tasks/gdp_us_const_trim.py

# Run ndbi_gee task
ndbi_gee:
  cd services/fetch_load_data/ && uv run tasks/ndbi_gee.py

# Run ndvi_gee task
ndvi_gee:
  cd services/fetch_load_data/ && uv run tasks/ndvi_gee.py

# Run precip task
precip:
  cd services/fetch_load_data/ && uv run tasks/precip.py

# Run temp_air task
temp_air:
  cd services/fetch_load_data/ && uv run tasks/temp_air.py

# Run temp_ls task
temp_ls:
  cd services/fetch_load_data/ && uv run tasks/temp_ls.py

# Run viirs_bm task
viirs_bm:
  cd services/fetch_load_data/ && uv run tasks/viirs_bm.py
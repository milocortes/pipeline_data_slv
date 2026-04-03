# Default recipe
default:
  just --list

# Run evi_gee task
evi_gee:
  uv run evi_gee.py

# Run gdp_us_const_trim task
gdp_us_const_trim:
  uv run gdp_us_const_trim.py

# Run ndbi_gee task
ndbi_gee:
  uv run ndbi_gee.py

# Run ndvi_gee task
ndvi_gee:
  uv run ndvi_gee.py

# Run precip task
precip:
  uv run precip.py

# Run temp_air task
temp_air:
  uv run temp_air.py

# Run temp_ls task
temp_ls:
  uv run temp_ls.py

# Run viirs_bm task
viirs_bm:
  uv run viirs_bm.py
#!/bin/bash

## Construye datos panel
echo "Construye datos panel"
uv run crea_pdata_bpvar.py 

## Ejecuta modelo
echo "Ejecuta modelo BPVARS"
Rscript bpvars.R

## Manda datos a Delta Lake
echo "Manda datos a Delta Lake"
uv run envia_delta_lake.py


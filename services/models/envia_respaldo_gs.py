## GS packages
import gspread
from google.oauth2.service_account import Credentials

## Disable Warnings
import warnings
warnings.filterwarnings("ignore")

## Carga rich
from rich.console import Console
console = Console()

## Carga lista de Tablas en GS
from utils import ALL_TABLES_GS, build_general_config, build_storage_config

import polars as pl
import numpy as np
import os

## Carga configuración
## Carga configuración general
config = build_general_config()

## Carga Configuración de almacenamiento
storage_options = build_storage_config()


# Authenticate
console.print("1.-", "Autenticando en GS", style="bold red")

GS_API_KEY_FILE = os.getenv("GS_API_KEY_FILE")

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(f'config/api_keys/{GS_API_KEY_FILE}', scopes=scopes)
client = gspread.authorize(creds)

# Open Google Sheet and update
SPREADSHEET = os.getenv("GS_SPREADSHEET")
sh = client.open(SPREADSHEET)

# Get all worksheets
worksheets = sh.worksheets()

# DELETE ALL SHEETS

# Prepare a batch update payload
# First, insert a fresh placeholder sheet at index 0.
# Then, append requests to delete all old worksheets.
requests = [{"addSheet": {"properties": {"title": "TempSheet", "index": 0}}}]

for sheet in worksheets:
    requests.append({"deleteSheet": {"sheetId": sheet.id}})

# Execute the batch operation
sh.batch_update({"requests": requests})
console.print("Successfully reset spreadsheet with a single blank sheet!")

#### Exportamos tablas de respaldos de los pronósticos a GS 
console.print("6.-", "Exportamos Tablas a GS", style="bold red")

for sheet_name in ALL_TABLES_GS:
    
    console.print("6.1-", f"Exportamos Tabla {sheet_name} a GS", style="bold red")

    # Cargamos Tabla de RustFS
    dato_respaldo = pl.read_delta(
        f"s3://{config['BUCKET_RESPALDO']}/{sheet_name}",
        storage_options=storage_options,
    ).to_pandas().replace(np.nan, "")
    
    # Create a new tab with 100 rows and 20 columns
    worksheet = sh.add_worksheet(
                    title=sheet_name, 
                    rows=2000, 
                    cols=30
                )

    # Upload data (headers + values)
    worksheet.update(
        [dato_respaldo.columns.values.tolist()] + dato_respaldo.values.tolist()
    )

# Elimina sheet temporal
worksheet_to_delete = sh.worksheet("TempSheet")

# Delete the worksheet from the spreadsheet
sh.del_worksheet(worksheet_to_delete)

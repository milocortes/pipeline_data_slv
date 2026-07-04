from typing import List, Dict
import os 
import socket
from deltalake import DeltaTable
import polars as pl 

## Función de construye el AWS_ENDPOINT_URL a partir del DNS del servidor y el puerto
def build_aws_endpoint_url() -> str :

    IP_DNS = socket.gethostbyname(os.getenv("RUSTFS_DNS"))
    PORT = os.getenv("RUSTFS_PORT")
    return f'http://{IP_DNS}:{PORT}'

## Método que construye diccionarios con las variables de ambiente de la configuración general
def build_general_config() -> Dict[str,str]:
    return {
        "start_date" : os.getenv("start_date"), 
        "LSIB" : os.getenv("LSIB"), 
        "BUCKET_NAME" : os.getenv("BUCKET_NAME"), 
        "service_account_gee" : os.getenv("service_account_gee"), 
        "gee_project" : os.getenv("gee_project")
    }

## Método que construye diccionarios con las variables de ambiente de la configuración del storage
def build_storage_config() -> Dict[str,str]:
    
    S3_AWS_STORAGE = os.getenv("S3_AWS_STORAGE")

    if  S3_AWS_STORAGE == 'True':
        return {
            'AWS_REGION': os.getenv("AWS_REGION"),
            'AWS_ACCESS_KEY_ID': os.getenv("AWS_ACCESS_KEY_ID"),
            'AWS_SECRET_ACCESS_KEY': os.getenv("AWS_SECRET_ACCESS_KEY"),
            #'AWS_S3_LOCKING_PROVIDER': 'dynamodb',
            #'DELTA_DYNAMO_TABLE_NAME': 'delta_log',
        }
    else:
        return {
            'AWS_ENDPOINT_URL': build_aws_endpoint_url(),
            'AWS_REGION': os.getenv("AWS_REGION"),
            'AWS_ACCESS_KEY_ID': os.getenv("AWS_ACCESS_KEY_ID"),
            'AWS_SECRET_ACCESS_KEY': os.getenv("AWS_SECRET_ACCESS_KEY"),
            'allow_http': os.getenv("allow_http")
        }

## Función que devuelve el token del provedor seleccionado
def get_token(provider : str):

    ## Carga configuración general
    config = build_general_config()

    ## Carga Configuración de almacenamiento
    storage_options = build_storage_config()

    ## Ruta en Delta Lake de la tabla de Tokens
    URL_DELTA_TABLE = f"s3://{config['BUCKET_NAME']}/fred_blackmarble_api_keys"

    ## Verifica si la Tabla existe:
    if DeltaTable.is_deltatable(URL_DELTA_TABLE, storage_options=storage_options):

        # Cargamos Tokens actuales
        df_tokens = pl.read_delta(
                f"s3://{config['BUCKET_NAME']}/fred_blackmarble_api_keys",
                storage_options=storage_options,
            )

        # Consultamos token 
        token = df_tokens.filter(provider=provider)["api_key"][0]

        return token

    else:
        return None
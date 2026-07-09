from typing import List, Dict
import os 
import socket

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
        "BUCKET_RESPALDO" : os.getenv("BUCKET_RESPALDO"), 
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
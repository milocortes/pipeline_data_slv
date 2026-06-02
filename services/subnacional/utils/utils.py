from typing import List, Dict
import os

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
    return {
        'AWS_ENDPOINT_URL': os.getenv("AWS_ENDPOINT_URL"),
        'AWS_REGION': os.getenv("AWS_REGION"),
        'AWS_ACCESS_KEY_ID': os.getenv("AWS_ACCESS_KEY_ID"),
        'AWS_SECRET_ACCESS_KEY': os.getenv("AWS_SECRET_ACCESS_KEY"),
        'allow_http': os.getenv("allow_http")
    }

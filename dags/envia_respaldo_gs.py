import os
from datetime import datetime

from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
#from docker.types import Mount
from utils import ENVS_VARS

with DAG(
    dag_id="respaldo_pronostico_gs",
    description="Envía Tablas de Pronóstico Respaldadas a GS.",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2030, 1, 3),
    max_active_tasks=1,  # Limits this DAG to 1 parallel tasks
    max_active_runs=1,    # Limits to 1 active run at a time
    #schedule=CronDataIntervalTimetable("@monthly", "UTC"),
    catchup=True,
):

    envia_respaldo = DockerOperator(
        task_id="docker_respaldo_pronostico_gs",
        image="models-dev:latest",
        command=[
            "uv", 
            "run", 
            "envia_respaldo_gs.py"
        ],
        # Explicitly forward the variable here:
        environment={
            ENV : os.environ.get(ENV) for ENV in ENVS_VARS
        },
        network_mode="pipeline_data_slv_default"
    )

    envia_respaldo
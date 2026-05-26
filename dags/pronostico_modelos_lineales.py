import os
from datetime import datetime

from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
#from docker.types import Mount

with DAG(
    dag_id="forecast_modelos_lineales",
    description="Pronóstico de Modelos Lineales usando Docker.",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2030, 1, 3),
    max_active_tasks=1,  # Limits this DAG to 1 parallel tasks
    max_active_runs=1,    # Limits to 1 active run at a time
    #schedule=CronDataIntervalTimetable("@monthly", "UTC"),
    catchup=True,
):
    forecast_arimax = DockerOperator(
        task_id="docker_forecast_modelos_lineales",
        image="models-test:latest",
        command=[
            "uv", 
            "run", 
            "arimax_models_rev.py"
        ],
        network_mode="host",
        # Note: this host path is on the HOST, not in the Airflow docker container.
        #mounts=[Mount(source="docker_airflow-data-volume", target="/data", type="volume")],
        #mount_tmp_dir=False,
    )

    forecast_arimax
import os
from datetime import datetime

from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
#from docker.types import Mount
from utils import ENVS_VARS

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

    forecast_arimax = KubernetesPodOperator(
        task_id="docker_forecast_modelos_lineales",
        #image="models-test:latest",
        image="models-dev:latest",
        cmds=[
            "uv", 
            "run", 
            "arimax_models_rev.py"
        ],
        # Explicitly forward the variable here:
        environment={
            ENV : os.environ.get(ENV) for ENV in ENVS_VARS
        },
        namespace="airflow",
        name="echo-docker",
        in_cluster=True,
        image_pull_policy="IfNotPresent",
        is_delete_operator_pod=True,
    )

    forecast_arimax
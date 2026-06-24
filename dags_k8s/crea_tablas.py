import os
from datetime import datetime

from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
from utils import ENVS_VARS

with DAG(
    dag_id="crea_tablas",
    description="Creación de tablas iniciales.",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2030, 1, 3),
    max_active_tasks=1,  # Limits this DAG to 1 parallel tasks
    max_active_runs=1,    # Limits to 1 active run at a time
    #schedule=CronDataIntervalTimetable("@monthly", "UTC"),
    catchup=True,
):

    crea_tablas = KubernetesPodOperator(
        task_id="k8s_crea_tablas",
        #image="models-test:latest",
        image="models-dev::1.0.0",
        cmds=[
            "uv", 
            "run", 
            "crea_tablas.py"
        ],
        # Explicitly forward the variable here:
        environment={
            ENV : os.environ.get(ENV) for ENV in ENVS_VARS
        },
        namespace="airflow",
        name="k8s_crea_tablas",
        in_cluster=True,
        image_pull_policy="IfNotPresent",
        is_delete_operator_pod=True,
    )

    crea_tablas
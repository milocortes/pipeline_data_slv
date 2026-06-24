import os
from datetime import datetime

from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
#from docker.types import Mount
from utils import ENVS_VARS

with DAG(
    dag_id="estimacion_subnacional",
    description="Estimación del PIB Subnacional usando Docker.",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2030, 1, 3),
    max_active_tasks=1,  # Limits this DAG to 1 parallel tasks
    max_active_runs=1,    # Limits to 1 active run at a time
    #schedule=CronDataIntervalTimetable("@monthly", "UTC"),
    catchup=True,
):
    subnacional = DockerOperator(
        task_id="docker_estimacion_subnacional",
        #image="subnacional-test:latest",
        image="subnacional-dev:latest",
        # Explicitly forward the variable here:
        environment={
            ENV : os.environ.get(ENV) for ENV in ENVS_VARS
        },
        #command=["bash", "run_subnacional.sh"],
        #network_mode="host",
        network_mode="pipeline_data_slv_default"
        # Note: this host path is on the HOST, not in the Airflow docker container.
        #mounts=[Mount(source="docker_airflow-data-volume", target="/data", type="volume")],
        #mount_tmp_dir=False,
    )

    subnacional
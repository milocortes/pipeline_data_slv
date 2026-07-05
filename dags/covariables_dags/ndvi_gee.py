import os
from datetime import datetime

from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
#from docker.types import Mount
from utils import ENVS_VARS

with DAG(
    dag_id="fetch_ndvi_gee",
    description="Fetches NDVI from the GEE API using Docker.",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2030, 1, 3),
    max_active_tasks=1,  # Limits this DAG to 1 parallel tasks
    max_active_runs=1,    # Limits to 1 active run at a time
    #schedule=CronDataIntervalTimetable("@monthly", "UTC"),
    catchup=True,
):
    fetch_ndvi_gee = DockerOperator(
        task_id="fetch_ndvi_gee",
        image="fetch_load_data-dev:latest",
        command=[
            "uv", 
            "run", 
            "tasks/ndvi_gee.py"
        ],
        # Explicitly forward the variable here:
        environment={
            ENV : os.environ.get(ENV) for ENV in ENVS_VARS
        },
        #network_mode="host",
        network_mode="pipeline_data_slv_default",
        # Note: this host path is on the HOST, not in the Airflow docker container.
        #mounts=[Mount(source="docker_airflow-data-volume", target="/data", type="volume")],
        #mount_tmp_dir=False,
    )

    fetch_ndvi_gee
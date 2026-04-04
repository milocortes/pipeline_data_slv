import os
from datetime import datetime

from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
#from docker.types import Mount

with DAG(
    dag_id="test_fetch_api_data",
    description="Fetches USA GDP from the FRED API using Docker.",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 3),
    schedule=CronDataIntervalTimetable("@daily", "UTC"),
    catchup=True,
):
    fetch_fred_usa_gdp = DockerOperator(
        task_id="fetch_usa_gdp",
        image="gee-test:latest",
        command=[
            "uv", 
            "run", 
            "tasks/gdp_us_const_trim.py"
        ],
        network_mode="host",
        # Note: this host path is on the HOST, not in the Airflow docker container.
        #mounts=[Mount(source="docker_airflow-data-volume", target="/data", type="volume")],
        #mount_tmp_dir=False,
    )

    fetch_fred_usa_gdp
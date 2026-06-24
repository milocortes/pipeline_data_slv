import os
from datetime import datetime

from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
from kubernetes.client import models as k8s

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
    subnacional = KubernetesPodOperator(
        task_id="k8s_estimacion_subnacional",
        image="subnacional:1.0.0",
        # Explicitly forward the variable here:
        environment={
            ENV : os.environ.get(ENV) for ENV in ENVS_VARS
        },
        # Fetch all variables from a config and secret natively
        env_from=[
            k8s.V1EnvFromSource(
                secret_ref=k8s.V1SecretEnvSource(name="secrets")
            ),
            k8s.V1EnvFromSource(
                config_map_ref=k8s.V1ConfigMapEnvSource(name="config")
            ),
        ],
        namespace="airflow",
        name="k8s_estimacion_subnacional",
        in_cluster=True,
        image_pull_policy="IfNotPresent",
        is_delete_operator_pod=True,
    )

    subnacional
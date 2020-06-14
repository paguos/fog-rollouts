import os

from fastapi import FastAPI

from k8s import K8SClient
from models import FogRollout

app = FastAPI()
in_cluster = os.getenv("IN_CLUSTER", False)


@app.get("/rollouts")
def list_rollouts(namespace: str = "default"):
    if in_cluster:
        k8s_client = K8SClient.from_service_account()
    else:
        k8s_client = K8SClient.from_file()

    rollouts = FogRollout.objects(k8s_client).filter(namespace=namespace)
    return {
        "fogrollouts":
            [{"name": r.name, "version": r.spec["version"]} for r in rollouts]
    }


@app.get("/rollouts/{rollout_name}")
def get_rollout(rollout_name: str, namespace: str = "default"):
    if in_cluster:
        k8s_client = K8SClient.from_service_account()
    else:
        k8s_client = K8SClient.from_file()

    return FogRollout.objects(k8s_client).filter(
        namespace=namespace).get(name=rollout_name).obj

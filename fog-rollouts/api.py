from fastapi import FastAPI

from clients import K8SApi
from models import FogRollout

app = FastAPI()


@app.get("/rollouts")
def list_rollouts(namespace: str = "default"):
    k8s_api = K8SApi.from_env()

    rollouts = FogRollout.objects(k8s_api).filter(namespace=namespace)
    return {
        "fogrollouts":
            [{"name": r.name, "version": r.spec["version"]} for r in rollouts]
    }


@app.get("/rollouts/{rollout_name}")
def get_rollout(rollout_name: str, namespace: str = "default"):
    k8s_api = K8SApi.from_env()

    return FogRollout.objects(k8s_api).filter(
        namespace=namespace).get(name=rollout_name).obj

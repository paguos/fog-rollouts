import os
import requests

from loguru import logger
from pykube import HTTPClient
from pykube import KubeConfig
from pykube.objects import NamespacedAPIObject

api_endpoint = os.getenv("FOG_ROLLOUTS_API_ENDPOINT")
source_namespace = os.getenv("FOG_ROLLOUTS_API_NAMESPACE", "default")
target_namespace = os.getenv("FOG_ROLLOUTS_NAMESPACE", "default")


class K8SClient:

    @staticmethod
    def api():
        return HTTPClient(KubeConfig.from_env())


class FogRolloutsAPI:

    @staticmethod
    def get(name: str) -> dict:
        r = requests.get(
            f"http://{api_endpoint}/rollouts/{name}",
            params={"namespace": source_namespace}
        )
        fog_rollout_data = r.json()

        fog_rollout_data["metadata"] = {
            "name": name, "namespace":  target_namespace
        }
        return fog_rollout_data

    @staticmethod
    def rollouts() -> dict:
        r = requests.get(
            f"http://{api_endpoint}/rollouts",
            params={"namespace": source_namespace}
        )
        return r.json()["fogrollouts"]


class FogRollout(NamespacedAPIObject):
    version = "paguos.io/v1alpha1"
    kind = "FogRollout"
    endpoint = "fogrollouts"

    @property
    def spec(self) -> dict:
        return self.obj["spec"]

    @property
    def rollout_version(self) -> str:
        return self.obj["spec"]["version"]


class RolloutsWatcher:

    def __init__(self, api: HTTPClient):
        self.api = api

    def _update_rollout(self, rollout: FogRollout):
        existing_rollout = FogRollout.objects(self.api).filter(
            namespace=target_namespace).get(name=rollout.name)
        if rollout.rollout_version != existing_rollout.rollout_version:
            logger.info(
                f"Updating from version '{existing_rollout.rollout_version}' to '{rollout.rollout_version}'..."
            )
            existing_rollout.obj = rollout.obj
            existing_rollout.update()
            logger.info("Updating done!")

    def run(self):
        logger.info("Getting list of fog rollouts ...")
        rollouts = FogRolloutsAPI.rollouts()

        for r in rollouts:
            rollout_name = r["name"]
            logger.info(f"Getting fog rollout {rollout_name} ...")
            rollout_data = FogRolloutsAPI.get(r["name"])
            rollout = FogRollout(self.api, rollout_data)
            logger.info(f"Getting fog rollout {rollout_name} ... done!")

            if not rollout.exists():
                logger.info(f"Creating fog rollout {rollout_name} ...")
                rollout.create()
                logger.info(f"Creating fog rollout {rollout_name} ... done!")
            else:
                logger.info(f"{rollout_name} rollout already exist!")
                self._update_rollout(rollout)

    def close(self):
        self.api.session.close()


watcher = RolloutsWatcher(K8SClient.api())
watcher.run()
watcher.close()

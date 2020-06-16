import os
import requests

from loguru import logger
from pprint import pprint
from pykube import HTTPClient
from pykube import KubeConfig
from pykube.objects import NamespacedAPIObject

api_endpoint = os.getenv("FOG_ROLLOUTS_API_ENDPOINT")
source_namespace = os.getenv("FOG_ROLLOUTS_API_NAMESPACE", "default")
target_namespace = os.getenv("FOG_ROLLOUTS_NAMESPACE", "default")


class FogRollout(NamespacedAPIObject):
    version = "paguos.io/v1alpha1"
    kind = "FogRollout"
    endpoint = "fogrollouts"

    @property
    def spec(self) -> dict:
        return self.obj["spec"]

    @staticmethod
    def get_from_api(name: str):
        r = requests.get(
            f"http://{api_endpoint}/rollouts/{name}",
            params={"namespace": source_namespace}
        )
        fog_rollout_data = r.json()
        fog_rollout_data["metadata"] = {
            "name": name, "namespace":  target_namespace
        }
        pprint(fog_rollout_data)
        return FogRollout(FogRollout._get_api(), fog_rollout_data)

    @staticmethod
    def list_from_api() -> dict:
        r = requests.get(
            f"http://{api_endpoint}/rollouts",
            params={"namespace": source_namespace}
        )
        logger.info(r.text)
        return r.json()

    @staticmethod
    def _get_api():
        return HTTPClient(KubeConfig.from_env())


logger.info("Getting list of fog rollouts ...")
rollouts = FogRollout.list_from_api()["fogrollouts"]

for r in rollouts:
    rollout_name = r["name"]
    logger.info(f"Getting fog rollout {rollout_name} ...")
    fog_rollout = FogRollout.get_from_api(r["name"])
    logger.info(f"Getting fog rollout {rollout_name} ... done!")

    logger.info(f"Saving fog rollout {rollout_name} ...")
    fog_rollout.create()
    logger.info(f"Saving fog rollout {rollout_name} ... done!")

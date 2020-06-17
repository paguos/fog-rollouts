import os
import requests

from loguru import logger
from pykube import HTTPClient
from pykube import KubeConfig
from pykube.objects import NamespacedAPIObject

cloud_api_endpoint = os.getenv("FOG_ROLLOUTS_API_CLOUD")
cloud_namespace = os.getenv("FOG_ROLLOUTS_API_NAMESPACE", "default")
layer_api_endpoint = os.getenv("FOG_ROLLOUTS_API_LAYER")
layer_namespace = os.getenv("FOG_ROLLOUTS_NAMESPACE", "default")


class K8SClient:

    @staticmethod
    def api():
        return HTTPClient(KubeConfig.from_env())


class FogRolloutsAPI:

    def __init__(self, api_endpoint, rollouts_namespace):
        self.api_endpoint = api_endpoint
        self.rollouts_namespace = rollouts_namespace

    @staticmethod
    def from_config(api_endpoint, rollouts_namespace):
        return FogRolloutsAPI(api_endpoint, rollouts_namespace)

    def get(self, name: str) -> dict:
        r = requests.get(
            f"http://{self.api_endpoint}/rollouts/{name}",
            params={"namespace": self.rollouts_namespace}
        )
        fog_rollout_data = r.json()

        fog_rollout_data["metadata"] = {
            "name": name, "namespace":  self.rollouts_namespace
        }
        return fog_rollout_data

    def rollouts(self) -> dict:
        r = requests.get(
            f"http://{self.api_endpoint}/rollouts",
            params={"namespace": self.rollouts_namespace}
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
        self.k8s_api = api
        self.cloud_api = FogRolloutsAPI.from_config(
            cloud_api_endpoint, cloud_namespace
        )
        self.layer_api = FogRolloutsAPI.from_config(
            layer_api_endpoint, layer_namespace
        )

    def _apply_rollout(self, rollout_metdata: dict):
        rollout_data = self.cloud_api.get(rollout_metdata["name"])
        rollout_data["metadata"]["namespace"] = layer_namespace
        rollout = FogRollout(self.k8s_api, rollout_data)
        if not rollout.exists():
            logger.info(f"Creating fog rollout {rollout_metdata['name']} ...")
            rollout.create()
            logger.info(
                f"Creating fog rollout {rollout_metdata['name']} ... done!")
        else:
            logger.info(f"{rollout_metdata['name']} rollout already exist!")
            self._update_rollout(rollout_metdata)

    def _delete_rollout(self, rollout_metadata: dict):
        layer_rollout = FogRollout.objects(
            self.k8s_api).filter(namespace=layer_namespace).get(
                name=rollout_metadata["name"]
        )
        layer_rollout.delete()

    def _update_rollout(self, rollout_metdata: dict):
        rollout_data = self.cloud_api.get(rollout_metdata["name"])
        rollout_data["metadata"]["namespace"] = layer_namespace
        cloud_rollout = FogRollout(self.k8s_api, rollout_data)
        layer_rollout = FogRollout.objects(self.k8s_api).filter(
            namespace=layer_namespace).get(name=rollout_metdata["name"])

        if cloud_rollout.rollout_version != layer_rollout.rollout_version:
            logger.info(
                f"Updating from version '{layer_rollout.rollout_version}' to '{cloud_rollout.rollout_version}'..."
            )
            layer_rollout.obj = cloud_rollout.obj
            layer_rollout.update()
            logger.info("Updating done!")

    def run(self):
        logger.info("Getting rollouts from the cloud ...")
        cloud_rollouts = self.cloud_api.rollouts()
        logger.info(f"Rollouts found in the cloud: {len(cloud_rollouts)}")

        logger.info("Getting rollouts from this layer ...")
        layer_rollouts = self.layer_api.rollouts()
        logger.info(f"Rollouts found in this layer: {len(layer_rollouts)}")

        logger.info("Synchronizing rollouts ...")
        for rollout in cloud_rollouts:
            if rollout not in layer_rollouts:
                self._apply_rollout(rollout)

        layer_rollouts = self.layer_api.rollouts()

        for rollout in layer_rollouts:
            if rollout not in cloud_rollouts:
                logger.info(f"Removing '{rollout['name']}' ...")
                self._delete_rollout(rollout)
                logger.info(f"Removing '{rollout['name']}' ... done!")
        logger.info("Rollouts synchronized!")

    def close(self):
        self.k8s_api.session.close()


watcher = RolloutsWatcher(K8SClient.api())
watcher.run()
watcher.close()

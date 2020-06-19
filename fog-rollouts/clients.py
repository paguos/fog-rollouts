import requests
from pykube import HTTPClient
from pykube import KubeConfig

from models import LayerConfig


class FogRolloutsAPI:

    def __init__(self, config: LayerConfig):
        self.config = config

    @staticmethod
    def from_config(config: LayerConfig):
        return FogRolloutsAPI(config)

    def get(self, name: str) -> dict:
        r = requests.get(f"http://{self.config.api_endpoint}/rollouts/{name}",
                         params={"namespace": self.config.namespace})
        fog_rollout_data = r.json()

        fog_rollout_data["metadata"] = {
            "name": name, "namespace":  self.config.namespace
        }
        return fog_rollout_data

    def rollouts(self) -> dict:
        r = requests.get(
            f"http://{self.config.api_endpoint}/rollouts",
            params={"namespace": self.config.namespace}
        )
        return r.json()["fogrollouts"]


class K8SApi:

    @ staticmethod
    def from_env():
        return HTTPClient(KubeConfig.from_env())

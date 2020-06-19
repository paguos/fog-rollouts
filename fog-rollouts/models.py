import os
from pykube.objects import NamespacedAPIObject


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


class LayerConfig:

    def __init__(self, layer, namespace, api_endpoint):
        self.layer = layer
        self.namespace = namespace
        self.api_endpoint = api_endpoint

    @staticmethod
    def from_env(layer: str):
        if layer == "cloud":
            api_endpoint = os.getenv("FOG_ROLLOUTS_CLOUD_API")
            namespace = os.getenv(
                "FOG_ROLLOUTS_CLOUD_NAMESPACE", "default")
        elif layer in ["fog", "edge"]:
            api_endpoint = os.getenv("FOG_ROLLOUTS_API")
            namespace = os.getenv(
                "FOG_ROLLOUTS_NAMESPACE", "default")
        else:
            raise NameError(
                f"Invalid layer name: {layer}."
                f"Must be 'cloud', 'edge' or 'fog'."
            )

        return LayerConfig(layer, namespace, api_endpoint)

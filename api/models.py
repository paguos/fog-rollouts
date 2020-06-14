from pykube.objects import NamespacedAPIObject


class FogRollout(NamespacedAPIObject):
    version = "paguos.io/v1alpha1"
    kind = "FogRollout"
    endpoint = "fogrollouts"

    @property
    def spec(self) -> dict:
        return self.obj["spec"]

    # def deployments(self) -> list:
    #     return self.obj["spec"]["deployments"]

    # def version(self) -> str:
    #     return self.obj["spec"]["version"]

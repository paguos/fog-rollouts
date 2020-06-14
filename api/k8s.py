from pathlib import Path
from pykube import HTTPClient
from pykube import KubeConfig


class K8SClient:

    @staticmethod
    def from_file(file_path=f"{Path.home()}/.kube/config"):
        return HTTPClient(
            KubeConfig.from_file("/Users/pabloosinaga/.kube/config")
        )

    @staticmethod
    def from_service_account():
        return HTTPClient(
            KubeConfig.from_env()
        )

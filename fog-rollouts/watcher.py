from loguru import logger

from clients import FogRolloutsAPI
from clients import K8SApi
from models import FogRollout
from models import LayerConfig


class FogRolloutsWatcher:

    def __init__(
        self,
        cloud_config: LayerConfig,
        layer_config: LayerConfig,
        k8s_api: K8SApi
    ):
        self.cloud_config = cloud_config
        self.layer_config = layer_config
        self.k8s_api = k8s_api

    @property
    def cloud_api(self) -> FogRolloutsAPI:
        return FogRolloutsAPI.from_config(self.cloud_config)

    @property
    def layer_api(self) -> FogRolloutsAPI:
        return FogRolloutsAPI.from_config(self.layer_config)

    @staticmethod
    def from_env():
        cloud_config = LayerConfig.from_env("cloud")
        layer_config = LayerConfig.from_env("fog")
        k8s_api = K8SApi.from_env()
        return FogRolloutsWatcher(cloud_config, layer_config, k8s_api)

    def _apply_rollout(self, rollout_metdata: dict):
        rollout_data = self.cloud_api.get(rollout_metdata["name"])
        rollout_data["metadata"]["namespace"] = self.layer_config.namespace
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
            self.k8s_api).filter(namespace=self.layer_config.namespace).get(
                name=rollout_metadata["name"]
        )
        layer_rollout.delete()

    def _update_rollout(self, rollout_metdata: dict):
        rollout_data = self.cloud_api.get(rollout_metdata["name"])
        rollout_data["metadata"]["namespace"] = self.layer_config.namespace
        cloud_rollout = FogRollout(self.k8s_api, rollout_data)
        layer_rollout = FogRollout.objects(self.k8s_api).filter(
            namespace=self.layer_config.namespace).get(name=rollout_metdata["name"])

        if cloud_rollout.rollout_version != layer_rollout.rollout_version:
            logger.info(
                f"Updating from version '{layer_rollout.rollout_version}'"
                f"to '{cloud_rollout.rollout_version}'..."
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


watcher = FogRolloutsWatcher.from_env()
watcher.run()
watcher.close()

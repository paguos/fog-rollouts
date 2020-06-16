import kopf
import os

from loguru import logger
from pykube import Deployment
from pykube import KubeConfig
from pykube import HTTPClient
from pykube import ObjectDoesNotExist

LAYER = os.getenv("FOG_ROLLOUTS_LAYER", "cloud")


def create_deployment_data(meta, spec):
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": f"{meta['name']}-{LAYER}"
        },
        "spec": {
            "replicas": spec["deployments"][LAYER]["replicas"],
            "selector": {"matchLabels": {"app": "test"}},
            "template": {
                "metadata": {"labels": {"app": "test"}},
                "spec": {
                    "containers": spec["deployments"][LAYER]["containers"]
                }
            }
        }
    }


@kopf.on.create('paguos.io', 'v1alpha1', 'fogrollouts')
def create_3(body, meta, spec, status, **kwargs):
    deployment_data = create_deployment_data(meta, spec)
    logger.info("Creating deployment ...")

    # Make it our child: assign the namespace, name, labels, owner references
    kopf.adopt(deployment_data)
    # kopf.label(pod_data, {'application': 'kopf-example-10'})

    # # Actually create an object by requesting the Kubernetes API.
    api = HTTPClient(KubeConfig.from_env())
    deployment = Deployment(api, deployment_data)
    deployment.create()
    api.session.close()

    logger.info("Creating deployment ... done!")

    return {'job1-status': 100}


@kopf.on.update('paguos.io', 'v1alpha1', 'fogrollouts')
def update(body, meta, spec, status, **kwargs):
    deployment_name = f"{meta['name']}-{LAYER}"
    api = HTTPClient(KubeConfig.from_env())
    logger.info(f"Updating deployment {deployment_name} ...")

    try:
        deployment = Deployment.objects(
            api).filter(
            namespace=meta["namespace"]).get(name=deployment_name)

        deployment.obj["spec"] = {
            "replicas": spec["deployments"][LAYER]["replicas"],
            "selector": {"matchLabels": {"app": "test"}},
            "template": {
                "metadata": {"labels": {"app": "test"}},
                "spec": {
                    "containers": spec["deployments"][LAYER]["containers"]
                }
            }
        }
        deployment.update()
    except ObjectDoesNotExist:
        logger.warning(f"Deployment {deployment_name} doesn't exist")
        deployment_data = create_deployment_data(meta, spec)

        logger.info("Creating deployment ...")
        kopf.adopt(deployment_data)
        deployment = Deployment(api, deployment_data)
        deployment.create()
        logger.info("Creating deployment ... done!")

    api.session.close()
    logger.info(f"Updating deployment {deployment_name} ... done!")
    return {'job1-status': 100}


@kopf.on.delete('paguos.io', 'v1alpha1', 'fogrollouts')
def delete(body, meta, spec, status, **kwargs):
    deployment_name = f"{meta['name']}-{LAYER}"
    api = HTTPClient(KubeConfig.from_env())
    logger.info(f"Deleting deployment {deployment_name} ...")

    try:
        deployment = Deployment.objects(
            api).filter(
            namespace=meta["namespace"]).get(name=deployment_name)
        deployment.delete()
    except ObjectDoesNotExist:
        logger.warning(f"Deployment {deployment_name} doesn't exist")

    api.session.close()
    logger.info(f"Deleting deployment {deployment_name} ... done!")
    return {'job1-status': 100}

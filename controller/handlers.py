import kopf
# import json
import yaml

from loguru import logger
from pykube import Deployment
from pykube import KubeConfig
from pykube import HTTPClient

LAYER = "cloud"


@kopf.on.create('paguos.io', 'v1alpha1', 'fogrollouts')
def create_fn_1(**kwargs):
    print('CREATED 1st')


@kopf.on.create('paguos.io', 'v1alpha1', 'fogrollouts')
def create_3(body, meta, spec, status, **kwargs):
    deployment_data = {
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

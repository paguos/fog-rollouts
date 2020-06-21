import kopf
import os

from loguru import logger
from pykube import Deployment
from pykube import Service
from pykube import ObjectDoesNotExist

from clients import K8SApi

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
            "selector": {"matchLabels": {"fog-rollout": f"{meta['name']}"}},
            "template": {
                "metadata": {"labels": {"fog-rollout": f"{meta['name']}"}},
                "spec": {
                    "containers": spec["deployments"][LAYER]["containers"]
                }
            }
        }
    }


def create_service_data(meta, spec):
    containers = [c
                  for c in spec["deployments"][LAYER]["containers"]]
    port_list = []
    for container in containers:
        ports = container["ports"]
        for port in ports:

            port_spec = {
                "port": port["containerPort"],
                "targetPort": port["containerPort"]
            }
            if "name" in port:
                port_spec["name"] = port["name"]

            port_list.append(port_spec)
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": f"{meta['name']}"
        },
        "spec": {
            "selector": {"fog-rollout": f"{meta['name']}"},
            "ports": port_list
        }
    }


@ kopf.on.create('paguos.io', 'v1alpha1', 'fogrollouts')
def create(body, meta, spec, status, **kwargs):
    api = K8SApi.from_env()

    logger.info("Creating deployment ...")
    deployment_data = create_deployment_data(meta, spec)
    kopf.adopt(deployment_data)
    # kopf.label(pod_data, {'application': 'kopf-example-10'})

    deployment = Deployment(api, deployment_data)
    if deployment.exists():
        deployment.update()
    else:
        deployment.create()
    logger.info("Creating deployment ... done!")

    logger.info("Creating service ...")
    service_data = create_service_data(meta, spec)
    kopf.adopt(service_data)

    service = Service(api, service_data)
    if service.exists():
        service.update()
    else:
        service.create()
    logger.info("Creating service ... done!")

    api.session.close()
    return {'job1-status': 100}


@ kopf.on.update('paguos.io', 'v1alpha1', 'fogrollouts')
def update(body, meta, spec, status, **kwargs):

    api = K8SApi.from_env()
    logger.info(f"Updating fog rollout {meta['name']} ...")

    deployment_data = create_deployment_data(meta, spec)
    kopf.adopt(deployment_data)
    deployment = Deployment(api, deployment_data)

    if deployment.exists():
        logger.info(f"Updating deployment {deployment.name} ...")
        deployment.update()
        logger.info(f"Updating deployment {deployment.name} ... done!")
    else:
        logger.warning(f"Deployment {deployment.name} doesn't exist")
        logger.info(f"Creating deployment {deployment.name} ...")
        deployment.create()
        logger.info(f"Creating deployment {deployment.name} ... done!")

    service_data = create_service_data(meta, spec)
    kopf.adopt(service_data)

    service = Service(api, service_data)

    if service.exists():
        logger.info(f"Updating service {service.name} ...")
        service.update()
        logger.info(f"Updating service {service.name} ... done!")
    else:
        logger.warning(f"Service {service.name} doesn't exist")
        logger.info(f"Creating service {service.name} ...")
        service.create()
        logger.info(f"Creating service {service.name} ... done!")

    logger.info(f"Updating fog rollout {meta['name']} ... done!")
    api.session.close()
    return {'job1-status': 100}


@ kopf.on.delete('paguos.io', 'v1alpha1', 'fogrollouts')
def delete(body, meta, spec, status, **kwargs):
    api = K8SApi.from_env()

    deployment_name = f"{meta['name']}-{LAYER}"
    logger.info(f"Deleting deployment {deployment_name} ...")

    try:
        deployment = Deployment.objects(
            api).filter(
            namespace=meta["namespace"]).get(name=deployment_name)
        deployment.delete()
    except ObjectDoesNotExist:
        logger.warning(f"Deployment {deployment_name} doesn't exist")

    logger.info(f"Deleting deployment {deployment_name} ... done!")

    service_name = f"{meta['name']}"
    logger.info(f"Deleting service {service_name} ...")

    try:
        service = Service.objects(
            api).filter(
            namespace=meta["namespace"]).get(name=service_name)
        service.delete()
    except ObjectDoesNotExist:
        logger.warning(f"Service {service_name} doesn't exist")

    logger.info(f"Deleting service {service_name} ... done!")
    api.session.close()
    return {'job1-status': 100}

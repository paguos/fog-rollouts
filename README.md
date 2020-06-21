# Fog Rollouts

Experimental deployment of applications in fog environments.

## Requirements

- [docker](https://www.docker.com/get-started) - container platform
- [helm](http://helm.sh) - kubernetes package manager
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) - kubernetes management tool
- [k3d](https://github.com/rancher/k3d) - containerized k3s kubernetes distribution
- [pipenv](https://pipenv.pypa.io/en/latest/) - python dependency manager

## Setup

Init a `k8s` cluster using `k3d`:

```sh
k3d create --image rancher/k3s:v1.18.2-k3s1
```

Set the config for your local `kubectl`:

```sh
export KUBECONFIG="$(k3d get-kubeconfig --name='k3s-default')"
```

Setup an environment with this three namespaces `cloud`, `fog` and `edge`:

```
make run
```

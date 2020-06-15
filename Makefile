build:
	docker build api -t fog-rollouts-api
	docker build controller -t fog-rollouts-controller

k3d/import:
	k3d import-images fog-rollouts-api fog-rollouts-controller

k8s/base:
	kubectl apply -f kubernetes/base

k8s/namespace:
	NAMESPACE=cloud ./scripts/namespace_apply.sh
	NAMESPACE=fog ./scripts/namespace_apply.sh

run: build k3d/import k8s/base k8s/namespace
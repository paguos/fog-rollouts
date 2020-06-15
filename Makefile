define helm_install
	kubectl create ns $1
    helm install fog-rollouts ./chart --namespace=$1
endef

build:
	docker build api -t fog-rollouts-api
	docker build controller -t fog-rollouts-controller

k3d/import:
	k3d import-images fog-rollouts-api fog-rollouts-controller

helm:
	$(call helm_install,cloud)
	$(call helm_install,fog)

clean:
	helm delete fog-rollouts --namespace=cloud
	helm delete fog-rollouts --namespace=fog


run: build k3d/import helm
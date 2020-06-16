build:
	docker build api -t fog-rollouts-api
	docker build controller -t fog-rollouts-controller

k3d/import:
	k3d import-images fog-rollouts-api fog-rollouts-controller

helm:
	helm install fog-rollouts ./chart --namespace=cloud --create-namespace
	helm install fog-rollouts ./chart --namespace=fog --create-namespace

clean:
	helm delete fog-rollouts --namespace=cloud
	helm delete fog-rollouts --namespace=fog


run: build k3d/import helm
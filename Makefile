build:
	docker build api -t fog-rollouts-api
	docker build controller -t fog-rollouts-controller
	docker build watcher -t fog-rollouts-watcher

k3d/import:
	k3d import-images fog-rollouts-api fog-rollouts-controller fog-rollouts-watcher

helm:
	helm install fog-rollouts ./chart --namespace=cloud --create-namespace
	helm install fog-rollouts ./chart --namespace=fog --create-namespace --set layer.name=fog,layer.api_endpoint=fog-rollouts-api.fog,cloud.api_endpoint=fog-rollouts-api.cloud,cloud.namespace=cloud

clean:
	helm delete fog-rollouts --namespace=cloud
	helm delete fog-rollouts --namespace=fog


run: build k3d/import helm
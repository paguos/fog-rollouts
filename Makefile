build:
	docker build . -t fog-rollouts

k3d/import:
	k3d import-images fog-rollouts

helm:
	helm install fog-rollouts ./chart --namespace=cloud --create-namespace
	helm install fog-rollouts ./chart --namespace=fog --create-namespace --set layer.name=fog,layer.api_endpoint=fog-rollouts-api.fog,cloud.api_endpoint=fog-rollouts-api.cloud,cloud.namespace=cloud
	helm install fog-rollouts ./chart --namespace=edge --create-namespace --set layer.name=edge,layer.api_endpoint=fog-rollouts-api.edge,cloud.api_endpoint=fog-rollouts-api.cloud,cloud.namespace=cloud

clean:
	helm delete fog-rollouts --namespace=cloud
	helm delete fog-rollouts --namespace=fog
	helm delete fog-rollouts --namespace=edge
	kubectl delete crd fogrollouts.paguos.io 


run: build k3d/import helm
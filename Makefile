build:
	docker build api -t fog-rollouts-api
	docker build controller -t fog-rollouts-controller

k3d/import:
	k3d import-images fog-rollouts-api fog-rollouts-controller

k3d/apply:
	kubectl apply -f kubernetes/base
	kubectl apply -f kubernetes/k3d

run: build k3d/import k3d/apply
kubectl create ns $NAMESPACE
kubectl apply -f kubernetes/k3d -n $NAMESPACE
#!/bin/bash

# Set namespace
NAMESPACE="model-serving"

# Get the backend service IP
BACKEND_IP=$(kubectl get svc txt2img-backend -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Backend IP: ${BACKEND_IP}"

# Update the secret with the backend IP
kubectl create configmap txt2img-secret \
  --namespace=${NAMESPACE} \
  --from-literal=NEXT_PUBLIC_BACKEND_URL="http://${BACKEND_IP}:8000" \
  --dry-run=client -o yaml | kubectl apply -n ${NAMESPACE} -f -

# Delete existing frontend pods to force recreation with new secret
kubectl delete pods -n ${NAMESPACE} -l app=txt2img-frontend

# Wait for new pods
echo "Waiting for frontend pods to restart..."
kubectl rollout status deployment/txt2img-frontend -n ${NAMESPACE}

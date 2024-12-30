#!/bin/bash

# Set namespace
NAMESPACE="model-serving"

# Get the backend service IP
BACKEND_IP=$(kubectl get svc txt2img-backend -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Backend IP: ${BACKEND_IP}"

# Update the secret with the new backend URL
kubectl get secret txt2img-credentials -n ${NAMESPACE} -o yaml | \
sed "s|NEXT_PUBLIC_BACKEND_URL:.*|NEXT_PUBLIC_BACKEND_URL: $(echo -n "http://${BACKEND_IP}:8000" | base64)|" | \
kubectl apply -f -

# Delete existing frontend pods to force recreation
kubectl delete pods -n ${NAMESPACE} -l app=txt2img-frontend

# Wait for new pods
echo "Waiting for frontend pods to restart..."
kubectl rollout status deployment/txt2img-frontend -n ${NAMESPACE}
#!/bin/bash

# Set namespace
NAMESPACE="model-serving"

# Get the backend service IP
BACKEND_IP=$(kubectl get svc txt2img-backend -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Backend IP: ${BACKEND_IP}"

# Update the secret with the backend IP
kubectl create secret generic txt2img-credentials \
  --namespace=${NAMESPACE} \
  --from-literal=CREDENTIAL_JSON_FILE_NAME="app/credentials/namsee_key.json" \
  --from-literal=STORAGE_BUCKET_NAME="${STORAGE_BUCKET_NAME}" \
  --from-literal=SECRET_KEY="${SECRET_KEY}" \
  --from-literal=DATABASE_ENGINE="${DATABASE_ENGINE}" \
  --from-literal=DATABASE_NAME="${DATABASE_NAME}" \
  --from-literal=DATABASE_USER="${DATABASE_USER}" \
  --from-literal=DATABASE_PASSWORD="${DATABASE_PASSWORD}" \
  --from-literal=DATABASE_HOST="${DATABASE_HOST}" \
  --from-literal=DATABASE_PORT="${DATABASE_PORT}" \
  --from-literal=NEXT_PUBLIC_BACKEND_URL="http://${BACKEND_IP}:8000" \
  --dry-run=client -o yaml | kubectl apply -n ${NAMESPACE} -f -

# Delete existing frontend pods to force recreation with new secret
kubectl delete pods -n ${NAMESPACE} -l app=txt2img-frontend

# Wait for new pods
echo "Waiting for frontend pods to restart..."
kubectl rollout status deployment/txt2img-frontend -n ${NAMESPACE}
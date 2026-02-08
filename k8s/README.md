# ReSearch Kubernetes Deployment Guide

## Prerequisites

- Kubernetes cluster (1.25+)
- `kubectl` configured
- Container registry access (Docker Hub, GCR, ECR, etc.)
- Neo4j Aura instance (or self-hosted Neo4j)

## Quick Start

```bash
# 1. Create namespace
kubectl apply -f namespace.yaml

# 2. Create secrets (edit secrets.yaml first with base64-encoded values)
kubectl apply -f secrets.yaml

# 3. Deploy PostgreSQL
kubectl apply -f postgres.yaml

# 4. Deploy backend
kubectl apply -f backend-deployment.yaml

# 5. Deploy frontend
kubectl apply -f frontend-deployment.yaml

# 6. Create ingress
kubectl apply -f ingress.yaml
```

## Build & Push Images

```bash
# Build images
docker build -t your-registry/research-backend:latest -f Dockerfile.backend .
docker build -t your-registry/research-frontend:latest -f Dockerfile.frontend \
  --build-arg REACT_APP_BACKEND_URL=https://api.yourdomain.com .

# Push to registry
docker push your-registry/research-backend:latest
docker push your-registry/research-frontend:latest
```

## Configuration

### Secrets

Before applying, encode your secrets:

```bash
echo -n 'your-jwt-secret' | base64
echo -n 'your-gemini-key' | base64
echo -n 'neo4j+s://xxx.databases.neo4j.io' | base64
```

Edit `secrets.yaml` with the encoded values.

### Scaling

```bash
# Scale backend
kubectl scale deployment research-backend -n research --replicas=3

# Scale frontend
kubectl scale deployment research-frontend -n research --replicas=2
```

### Monitoring

```bash
# Check pod status
kubectl get pods -n research

# View backend logs
kubectl logs -f deployment/research-backend -n research

# View frontend logs
kubectl logs -f deployment/research-frontend -n research
```

## Architecture

```
                    ┌─────────────┐
                    │   Ingress   │
                    │  Controller │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    ┌──────────────────┐     ┌──────────────────┐
    │ Frontend Service │     │ Backend Service  │
    │   (ClusterIP)    │     │   (ClusterIP)    │
    │   Port: 3000     │     │   Port: 8001     │
    └────────┬─────────┘     └────────┬─────────┘
             │                        │
    ┌────────┴─────────┐     ┌────────┴─────────┐
    │ Frontend Pods    │     │ Backend Pods     │
    │ (nginx + React)  │     │ (FastAPI)        │
    │ Replicas: 2      │     │ Replicas: 2      │
    └──────────────────┘     └────────┬─────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                 ┌────────┴────────┐    ┌─────────┴────────┐
                 │ PostgreSQL Pod  │    │ Neo4j Aura       │
                 │ (StatefulSet)   │    │ (External)       │
                 │ + PVC           │    │                  │
                 └─────────────────┘    └──────────────────┘
```

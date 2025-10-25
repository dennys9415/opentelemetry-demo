# Deployment Guide

This guide covers deploying the OpenTelemetry Demo application in various environments, from development to production.

## Deployment Overview

The application can be deployed in several ways:

1. **Local Development** - Docker Compose (default)
2. **Production** - Docker Compose or Kubernetes
3. **Cloud Platforms** - AWS, GCP, Azure
4. **Hybrid** - Mixed environments

## 1. Local Development Deployment

### Using Docker Compose (Default)

```bash
# Clone the repository
git clone https://github.com/your-username/opentelemetry-demo.git
cd opentelemetry-demo

# Deploy with Docker Compose
docker-compose up -d

# Verify deployment
docker-compose ps
./scripts/health-check.sh
```

### Using Make Commands

```bash
make setup    # Full setup with health checks
make start    # Start services
make stop     # Stop services
make clean    # Clean up everything
```

## 2. Production Deployment

### Production Docker Compose

For production, use the production-optimized configuration:

```bash
# Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker-compose.prod.yml (create this file):

yaml
version: '3.8'

services:
  frontend:
    environment:
      - NODE_ENV=production
      - OTEL_SERVICE_NAME=frontend-service-prod
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    environment:
      - NODE_ENV=production
      - OTEL_SERVICE_NAME=backend-service-prod
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  database:
    restart: unless-stopped
    command: postgres -c shared_preload_libraries=pg_stat_statements -c pg_stat_statements.track=all
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  collector:
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  jaeger:
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  prometheus:
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  grafana:
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Production Environment Variables

Create a .env.production file:

```env
# Application
NODE_ENV=production
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:pass@database:5432/demo_db
POSTGRES_PASSWORD=your_secure_password_here

# OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317
OTEL_SERVICE_NAME=opentelemetry-demo-prod

# Security
SECRET_KEY=your_secret_key_here
```

## 3. Kubernetes Deployment

### Prerequisites

* Kubernetes cluster (v1.24+)
* kubectl configured
* Helm (optional)

### Basic Kubernetes Manifests

Create k8s/namespace.yaml:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: opentelemetry-demo
  labels:
    name: opentelemetry-demo
```

Create k8s/configmap.yaml:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: opentelemetry-demo-config
  namespace: opentelemetry-demo
data:
  otel-collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    exporters:
      logging:
        loglevel: debug
      jaeger:
        endpoint: jaeger:14250
        tls:
          insecure: true
    service:
      pipelines:
        traces:
          receivers: [otlp]
          exporters: [jaeger, logging]
```

Create k8s/secrets.yaml:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: opentelemetry-demo-secrets
  namespace: opentelemetry-demo
type: Opaque
data:
  database-password: <base64-encoded-password>
  secret-key: <base64-encoded-secret>
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (update with your values)
kubectl apply -f k8s/secrets.yaml

# Deploy applications
kubectl apply -f k8s/
```

## 4. Cloud-Specific Deployments

### AWS ECS Deployment

Create aws/task-definition.json:

```json
{
  "family": "opentelemetry-demo",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "your-registry/opentelemetry-demo-frontend:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/opentelemetry-demo",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "frontend"
        }
      }
    }
  ]
}
```

### Google Cloud Run

Create gcp/cloud-run.yaml:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: opentelemetry-demo-frontend
  namespace: default
spec:
  template:
    spec:
      containers:
      - image: gcr.io/your-project/opentelemetry-demo-frontend:latest
        ports:
        - containerPort: 8080
        env:
        - name: NODE_ENV
          value: "production"
        - name: BACKEND_URL
          value: "https://your-backend-service.a.run.app"
```

## 5. Monitoring and Observability

### Health Checks

All services include health endpoints:

* Frontend: GET /health
* Backend: GET /health

### Metrics Endpoints

* Prometheus: GET /metrics (if configured)
* Application metrics available at /metrics

### Logging Configuration

Configure logging for production:

```yaml
# In docker-compose.prod.yml
services:
  frontend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service_name"
```

## 6. Security Considerations

### Network Security

```yaml
# Example network segmentation
services:
  frontend:
    networks:
      - public
  backend:
    networks:
      - public
      - private
  database:
    networks:
      - private
```

### Secret Management

Use Docker secrets or Kubernetes secrets:

```bash
# Docker Swarm
echo "mysecretpassword" | docker secret create db_password -

# Kubernetes
kubectl create secret generic db-password --from-literal=password=mysecretpassword
```

## 7. Scaling Configuration

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  frontend:
    deploy:
      replicas: 3
    environment:
      - NODE_ENV=production
  backend:
    deploy:
      replicas: 2
    environment:
      - NODE_ENV=production
```

### Resource Limits

```yaml
services:
  frontend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

## 8. Backup and Recovery

### Database Backups

```bash
# Backup script
#!/bin/bash
docker-compose exec database pg_dump -U demo_user demo_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T database psql -U demo_user demo_db < backup_file.sql
```

### Configuration Backups

* Version control all configuration files
* Backup Docker volumes
* Export Grafana dashboards

## 9. Troubleshooting Production Issues

### Common Issues

1. Memory leaks: Monitor container memory usage
2. Database connections: Check connection pool settings
3. Network timeouts: Verify service discovery
4. Tracing data loss: Check collector buffer settings

### Debug Commands

```bash
# Check service status
docker-compose ps
kubectl get pods -n opentelemetry-demo

# View logs
docker-compose logs -f frontend
kubectl logs -f deployment/frontend -n opentelemetry-demo

# Check resource usage
docker stats
kubectl top pods -n opentelemetry-demo
```

## 10. Continuous Deployment

### GitHub Actions Example

Create .github/workflows/deploy.yml:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        ./scripts/deploy.sh production
      env:
        DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

This deployment guide covers the essential aspects of deploying the OpenTelemetry Demo application in various environments. Always test deployments in a staging environment before promoting to production.
#!/bin/bash

# Health check script for OpenTelemetry Demo

set -e

echo "Starting health checks..."

# Function to check service health
check_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "Checking $service at $url"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✓ $service is healthy"
            return 0
        fi
        
        echo "Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "✗ $service failed to become healthy"
    return 1
}

# Check all services
check_service "Frontend" "http://localhost:8080/health"
check_service "Backend" "http://localhost:5000/health"
check_service "Jaeger" "http://localhost:16686"
check_service "Zipkin" "http://localhost:9411/zipkin/"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3000/api/health"

echo "All services are healthy!"
echo ""
echo "Access URLs:"
echo "Frontend:      http://localhost:8080"
echo "Jaeger UI:     http://localhost:16686"
echo "Zipkin UI:     http://localhost:9411"
echo "Prometheus:    http://localhost:9090"
echo "Grafana:       http://localhost:3000 (admin/admin)"
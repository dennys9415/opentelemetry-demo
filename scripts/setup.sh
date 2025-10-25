#!/bin/bash

# Setup script for OpenTelemetry Demo

set -e

echo "Setting up OpenTelemetry Demo..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p data

# Build and start services
echo "Building and starting services..."
docker-compose build
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Run health checks
./scripts/health-check.sh

echo ""
echo "OpenTelemetry Demo setup completed successfully!"
echo "Run 'make stop' to stop all services"
echo "Run 'make clean' to remove all containers and volumes"
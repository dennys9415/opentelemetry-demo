# Getting Started with OpenTelemetry Demo

This guide will help you set up and run the OpenTelemetry Demo application on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** version 20.10+ [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** version 2.0+ [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Git** [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Optional Development Tools
- **Node.js** 16+ (for frontend development)
- **Python** 3.8+ (for backend development)
- **curl** or **Postman** (for API testing)

## Quick Start

### Method 1: Using Make (Recommended)

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/opentelemetry-demo.git
cd opentelemetry-demo
```

2. **Run the setup script:**

```bash
make setup
```

This will:

- Build all Docker images
- Start all services
- Run health checks
- Display access URLs

## Method 2: Manual Docker Compose

1. Clone and navigate:

```bash
git clone https://github.com/your-username/opentelemetry-demo.git
cd opentelemetry-demo
```

2. Build and start services:

```bash
docker-compose up -d
```

3. Check service status:

```bash
docker-compose ps
```

4. Run health checks:

```bash
./scripts/health-check.sh
```

## Verifying the Installation

After starting the services, you should have access to:

| Service	    | URL	                    | Purpose                           |
|---------------|---------------------------|-----------------------------------|
| Frontend      | http://localhost:8080	    | Web interface and API gateway     |
| Backend API	| http://localhost:5000	    | Backend service direct access     |
| Jaeger UI	    | http://localhost:16686	| Distributed tracing visualization |
| Zipkin UI	    | http://localhost:9411	    | Alternative tracing UI            |
| Prometheus	| http://localhost:9090	    | Metrics dashboard                 |
| Grafana	    | http://localhost:3000	    | Advanced metrics visualization    |
---

Default Grafana credentials:

* Username: admin
* Password: admin

## Testing the Application

### Using the Web Interface

1. Open http://localhost:8080 in your browser

2. You'll see a simple web interface with buttons to:

- Get users
- Create new users
- Get products
- Create orders

3. Click the buttons to generate traffic and traces

### Using the API Directly

```bash
# Get all users
curl http://localhost:8080/api/users

# Create a new user
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Get products
curl http://localhost:8080/api/products

# Create an order
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

## Viewing Traces

### Using Jaeger

1. Open http://localhost:16686
2. Select frontend-service or backend-service from the service dropdown
3. Click "Find Traces"
4. You should see traces from your API calls

### Using Zipkin

1. Open http://localhost:9411
2. You can search for traces by service name or other attributes

### Generating Load for Demonstration

To see more interesting traces, you can generate some load:

```bash
# Generate multiple requests
for i in {1..10}; do
  curl -X POST http://localhost:8080/api/users \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"User $i\", \"email\": \"user$i@example.com\"}" &
done

# Wait for all requests to complete
wait
```

## Common Issues and Solutions

### Port Conflicts

If you get port conflicts, you can change the ports in docker-compose.yml:

```yaml
services:
  frontend:
    ports:
      - "8081:8080"  # Change 8081 to your preferred port
```

## Docker Resource Issues

If Docker runs out of resources:

```bash
# Clean up unused containers and images
docker system prune

# Increase Docker memory allocation (Docker Desktop)
# Settings -> Resources -> Memory
```

## Services Not Starting

If services fail to start:

```bash
# Check logs for specific service
docker-compose logs frontend
docker-compose logs backend

# Restart services
docker-compose restart
```

## Stopping the Application

### Stop and Keep Data

```bash
docker-compose down
```

### Stop and Remove All Data

```bash
docker-compose down -v
```

### Full Cleanup

```bash
make clean
```

## Next Steps

* Read the Architecture Documentation to understand the system design
* Check the Development Guide to start contributing
* Explore the Deployment Guide for production setup

## Getting Help

If you encounter issues:

1. Check the service logs: docker-compose logs [service-name]
2. Verify all services are running: docker-compose ps
3. Run health checks: ./scripts/health-check.sh
4. Check the GitHub Issues for known problems

## Troubleshooting

### Health Checks Fail

If health checks fail, wait a bit longer and try again:

```bash
# Wait 30 seconds then retry
sleep 30
./scripts/health-check.sh
```

### No Traces in Jaeger

If you don't see traces in Jaeger:

1. Verify you've made some API calls
2. Check the collector logs: docker-compose logs collector
3. Ensure trace propagation is working

### Database Connection Issues

If you see database connection errors:

```bash
# Restart the database service
docker-compose restart database
```

This should get you up and running with the OpenTelemetry Demo application!
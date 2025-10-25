# Development Guide

This guide provides comprehensive information for developers working on the OpenTelemetry Demo application.

## Development Environment Setup

### Prerequisites

- **Docker** and **Docker Compose**
- **Node.js** 16+ (for frontend development)
- **Python** 3.8+ (for backend development)
- **Git**

### Initial Setup

1. **Clone the repository**:

```bash
git clone https://github.com/your-username/opentelemetry-demo.git
cd opentelemetry-demo
```

2.  Set up development environment:

```bash
# Using Make
make setup

# Or manually
docker-compose up -d
./scripts/health-check.sh
```

3. Install development dependencies:

```bash
# Frontend dependencies
cd src/frontend && npm install

# Backend dependencies
cd src/backend && pip install -r requirements.txt
```

## Project Structure

```text
opentelemetry-demo/
├── src/                    # Source code
│   ├── frontend/          # Node.js/Express frontend
│   ├── backend/           # Python/Flask backend
│   └── shared/            # Shared utilities
├── tests/                 # Test suites
├── deployments/           # Deployment configurations
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── docker-compose.yml     # Development environment
```

## Development Workflow

### 1. Running Services in Development Mode

Option A: Docker Development (Recommended)

```bash
# Start all services with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

docker-compose.dev.yml:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./src/frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./src/frontend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    command: npm run dev

  backend:
    build:
      context: ./src/backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./src/backend:/app
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    command: python app.py
```

Option B: Native Development

```bash
# Terminal 1 - Backend
cd src/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

# Terminal 2 - Frontend
cd src/frontend
npm install
npm run dev
```

### 2. Making Changes

Backend Development (Python/Flask)

File: src/backend/app.py

```python
@app.route('/api/new-endpoint', methods=['GET'])
def new_endpoint():
    with tracer.start_as_current_span("new_endpoint"):
        # Your code here
        return jsonify({"message": "Hello World"})
```

Adding Dependencies:

```bash
# Add to src/backend/requirements.txt
new-package==1.0.0
```

Frontend Development (Node.js/Express)

File: src/frontend/server.js

```javascript
app.get('/api/new-route', async (req, res) => {
  const span = tracer.startSpan('frontend-new-route');
  try {
    // Your code here
    res.json({ message: 'Hello from frontend' });
  } finally {
    span.end();
  }
});
```

Adding Dependencies:

```bash
cd src/frontend
npm install new-package
```

### 3. Testing Changes

Running Tests

```bash
# Backend tests
cd src/backend && pytest

# Frontend tests
cd src/frontend && npm test

# All tests
make test

# Integration tests
pytest tests/test_integration.py
```

Writing Tests

Backend Test Example:

```python
def test_new_endpoint(client):
    response = client.get('/api/new-endpoint')
    assert response.status_code == 200
    assert response.json['message'] == 'Hello World'
```

Frontend Test Example:

```javascript
describe('New Route', () => {
  it('should return hello message', async () => {
    const response = await request(app).get('/api/new-route');
    expect(response.status).toBe(200);
    expect(response.body.message).toBe('Hello from frontend');
  });
});
```

## OpenTelemetry Development

### Understanding Tracing

The application uses OpenTelemetry for distributed tracing. Key concepts:

* Spans: Represent individual operations
* Traces: Collection of related spans
* Context Propagation: Passing trace information between services

### Adding Custom Spans

Backend (Python):

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def some_operation():
    with tracer.start_as_current_span("custom_operation") as span:
        span.set_attribute("custom.attribute", "value")
        # Your operation here
```

Frontend (Node.js):

```javascript
const { trace } = require('@opentelemetry/api');
const tracer = trace.getTracer('frontend-service');

function someOperation() {
  const span = tracer.startSpan('custom_operation');
  span.setAttribute('custom.attribute', 'value');
  try {
    // Your operation here
  } finally {
    span.end();
  }
}
```

#### Custom Instrumentation

Creating Custom Instrumentation:

```python
# src/backend/custom_instrumentation.py
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

class CustomInstrumentation(BaseInstrumentor):
    def instrumentation_dependencies(self):
        return []

    def _instrument(self, **kwargs):
        # Your instrumentation logic
        pass

    def _uninstrument(self, **kwargs):
        # Your uninstrumentation logic
        pass
```

## Database Development

### Schema Changes

1. Modify initialization script (src/database/init.sql):

```sql
-- Add new table
CREATE TABLE IF NOT EXISTS new_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
```

2. Update models (src/backend/models.py):

```python
class NewModel:
    def __init__(self, name):
        self.name = name
```

3. Test migrations:

```bash
docker-compose down -v
docker-compose up -d
```

## Debugging

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend

# With timestamps
docker-compose logs -f --timestamps
```

### Debugging Traces

1. Check Jaeger UI: http://localhost:16686
2. Check Zipkin UI: http://localhost:9411
3. View collector logs: docker-compose logs -f collector

### Debugging in VS Code

Create .vscode/launch.json:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Backend",
      "type": "python",
      "request": "launch",
      "program": "src/backend/app.py",
      "console": "integratedTerminal",
      "env": {
        "FLASK_ENV": "development"
      }
    }
  ]
}
```

## Performance Optimization

### Database Optimization

Add indexes:

```sql
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

Query optimization:

```python
# Use efficient queries
cur.execute('SELECT id, name FROM users WHERE email = %s', (email,))
```

### Caching Strategies

Redis integration (optional):

```python
import redis

redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_cached_users():
    cached = redis_client.get('users')
    if cached:
        return json.loads(cached)
    # Otherwise, fetch from database and cache
```

## Code Quality

### Linting and Formatting

```bash
# Backend
cd src/backend
black .
flake8 .
mypy .

# Frontend
cd src/frontend
npm run lint
npx prettier --write .
```

### Pre-commit Hooks

Create .pre-commit-config.yaml:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

Install pre-commit:

```bash
pip install pre-commit
pre-commit install
```

## Adding New Features

### Feature Development Process

1. Create a feature branch:

```bash
git checkout -b feature/new-feature
```

2. Implement the feature with tests
3. Update documentation
4. Submit pull request

### Example: Adding a New Service

1. Create service directory:

```bash
mkdir src/new-service
```

2. Add Dockerfile and code
3. Update docker-compose.yml
4. Add to health checks
5. Update documentation

## Monitoring Development

### Development Metrics

Access development metrics:

* Prometheus: http://localhost:9090
* Grafana: http://localhost:3000 (admin/admin)

### Custom Metrics

Adding custom metrics:

```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('app_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Request duration')

@app.route('/api/metrics-endpoint')
def metrics_endpoint():
    REQUEST_COUNT.inc()
    with REQUEST_DURATION.time():
        # Your logic here
        pass
```

## Troubleshooting Development Issues

### Common Problems

1. Port conflicts: Change ports in docker-compose.yml
2. Docker build failures: Clear Docker cache docker system prune
3. Database connection issues: Check docker-compose logs database
4. Missing dependencies: Run make setup again

### Reset Development Environment

```bash
# Complete reset
make clean
make setup

# Partial reset
docker-compose down
docker-compose up -d
```

## Contributing

### Code Review Process

1. Ensure all tests pass
2. Update documentation
3. Follow code style guidelines
4. Add appropriate logging and tracing

### Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release tag
4. Deploy to staging
5. Deploy to production

This development guide should help you work effectively with the OpenTelemetry Demo codebase. For specific questions, check the documentation or create an issue in the repository.
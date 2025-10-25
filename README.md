# OpenTelemetry Demo - Distributed Tracing Application

[![CI](https://github.com/your-username/opentelemetry-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/opentelemetry-demo/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A comprehensive demo application demonstrating distributed tracing with OpenTelemetry across microservices.

```
opentelemetry-demo/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── release.yml
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
├── src/
│   ├── frontend/
│   │   ├── package.json
│   │   ├── server.js
│   │   ├── public/
│   │   │   └── index.html
│   │   └── Dockerfile
│   ├── backend/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── models.py
│   │   └── Dockerfile
│   ├── database/
│   │   └── init.sql
│   └── shared/
│       └── utils.py
├── docs/
│   ├── getting-started.md
│   ├── architecture.md
│   ├── development.md
│   └── deployment.md
├── deployments/
│   ├── otel-collector-config.yaml
│   ├── prometheus.yml
│   └── grafana-dashboard.yml
├── scripts/
│   ├── health-check.sh
│   ├── setup.sh
│   └── deploy.sh
├── tests/
│   ├── __init__.py
│   ├── test_backend.py
│   ├── test_integration.py
│   └── frontend/
│       └── test_app.js
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── docker-compose.yml
├── requirements.txt
├── package.json
└── Makefile
```

## 🚀 Features

- **Distributed Tracing**: End-to-end tracing across multiple services
- **Multiple Languages**: Demo services in Python, Node.js, and Java
- **Observability**: Integrated with Jaeger, Zipkin, and Prometheus
- **Microservices Architecture**: Real-world distributed system example
- **Docker Support**: Easy deployment with Docker Compose

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.8+
- Node.js 16+
- Java 11+

## 🛠 Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/opentelemetry-demo.git
cd opentelemetry-demo

# Start all services
docker-compose up -d

# Or use the Makefile
make start
```

The application will be available at:

* Frontend: http://localhost:8080
* Jaeger UI: http://localhost:16686
* Zipkin UI: http://localhost:9411
* Prometheus: http://localhost:9090

## 🏗 Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │───▶│   Backend   │───▶│  Database   │
│  (Node.js)  │    │   (Python)  │    │ (PostgreSQL)│
└─────────────┘    └─────────────┘    └─────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                 ┌────────▼────────┐
                 │  OpenTelemetry  │
                 │   Collector     │
                 └─────────────────┘
                          │
          ┌───────────────┼───────────────┐
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │   Jaeger  │   │  Zipkin   │   │ Prometheus│
    └───────────┘   └───────────┘   └───────────┘
```

## 📚 Documentation

* Getting Started
* Architecture Overview
* Development Guide
* Deployment Guide

## 🤝 Contributing

We welcome contributions! Please see our Contributing Guide and read our Code of Conduct.

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
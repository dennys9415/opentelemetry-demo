const express = require('express');
const axios = require('axios');
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// Initialize OpenTelemetry
const provider = new NodeTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'frontend-service',
  }),
});

const exporter = new OTLPTraceExporter({
  url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://collector:4318/v1/traces',
});

provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
provider.register();

const { trace } = require('@opentelemetry/api');
const tracer = trace.getTracer('frontend-service');

const app = express();
const PORT = process.env.PORT || 8080;
const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:5000';

app.use(express.json());
app.use(express.static('public'));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'frontend' });
});

// Get all users
app.get('/api/users', async (req, res) => {
  const span = tracer.startSpan('frontend-get-users');
  
  try {
    span.setAttribute('http.method', 'GET');
    span.setAttribute('http.route', '/api/users');
    
    const response = await axios.get(`${BACKEND_URL}/api/users`);
    span.setAttribute('http.status_code', response.status);
    
    res.json(response.data);
  } catch (error) {
    span.setAttribute('http.status_code', 500);
    span.recordException(error);
    res.status(500).json({ error: 'Failed to fetch users' });
  } finally {
    span.end();
  }
});

// Create a new user
app.post('/api/users', async (req, res) => {
  const span = tracer.startSpan('frontend-create-user');
  
  try {
    span.setAttribute('http.method', 'POST');
    span.setAttribute('http.route', '/api/users');
    
    const response = await axios.post(`${BACKEND_URL}/api/users`, req.body);
    span.setAttribute('http.status_code', response.status);
    
    res.status(201).json(response.data);
  } catch (error) {
    span.setAttribute('http.status_code', error.response?.status || 500);
    span.recordException(error);
    res.status(error.response?.status || 500).json({ 
      error: 'Failed to create user',
      details: error.response?.data 
    });
  } finally {
    span.end();
  }
});

// Get all products
app.get('/api/products', async (req, res) => {
  const span = tracer.startSpan('frontend-get-products');
  
  try {
    span.setAttribute('http.method', 'GET');
    span.setAttribute('http.route', '/api/products');
    
    const response = await axios.get(`${BACKEND_URL}/api/products`);
    span.setAttribute('http.status_code', response.status);
    
    res.json(response.data);
  } catch (error) {
    span.setAttribute('http.status_code', 500);
    span.recordException(error);
    res.status(500).json({ error: 'Failed to fetch products' });
  } finally {
    span.end();
  }
});

// Create an order
app.post('/api/orders', async (req, res) => {
  const span = tracer.startSpan('frontend-create-order');
  
  try {
    span.setAttribute('http.method', 'POST');
    span.setAttribute('http.route', '/api/orders');
    
    const response = await axios.post(`${BACKEND_URL}/api/order`, req.body);
    span.setAttribute('http.status_code', response.status);
    
    res.status(201).json(response.data);
  } catch (error) {
    span.setAttribute('http.status_code', error.response?.status || 500);
    span.recordException(error);
    res.status(error.response?.status || 500).json({ 
      error: 'Failed to create order',
      details: error.response?.data 
    });
  } finally {
    span.end();
  }
});

// Demo page
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenTelemetry Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
            button { padding: 10px 15px; margin: 5px; cursor: pointer; }
            .result { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>OpenTelemetry Demo Frontend</h1>
            
            <div class="card">
                <h2>Users</h2>
                <button onclick="getUsers()">Get Users</button>
                <button onclick="createUser()">Create User</button>
                <div id="usersResult" class="result"></div>
            </div>
            
            <div class="card">
                <h2>Products</h2>
                <button onclick="getProducts()">Get Products</button>
                <div id="productsResult" class="result"></div>
            </div>
            
            <div class="card">
                <h2>Orders</h2>
                <button onclick="createOrder()">Create Order</button>
                <div id="ordersResult" class="result"></div>
            </div>
        </div>

        <script>
            async function getUsers() {
                try {
                    const response = await fetch('/api/users');
                    const data = await response.json();
                    document.getElementById('usersResult').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('usersResult').innerHTML = 'Error: ' + error;
                }
            }

            async function createUser() {
                const user = {
                    name: 'New User ' + Date.now(),
                    email: 'user' + Date.now() + '@example.com'
                };
                
                try {
                    const response = await fetch('/api/users', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(user)
                    });
                    const data = await response.json();
                    document.getElementById('usersResult').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('usersResult').innerHTML = 'Error: ' + error;
                }
            }

            async function getProducts() {
                try {
                    const response = await fetch('/api/products');
                    const data = await response.json();
                    document.getElementById('productsResult').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('productsResult').innerHTML = 'Error: ' + error;
                }
            }

            async function createOrder() {
                const order = {
                    product_id: 1,
                    quantity: 2
                };
                
                try {
                    const response = await fetch('/api/orders', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(order)
                    });
                    const data = await response.json();
                    document.getElementById('ordersResult').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('ordersResult').innerHTML = 'Error: ' + error;
                }
            }
        </script>
    </body>
    </html>
  `);
});

app.listen(PORT, () => {
  console.log(`Frontend service running on port ${PORT}`);
  console.log(`OpenTelemetry endpoint: ${process.env.OTEL_EXPORTER_OTLP_ENDPOINT}`);
});
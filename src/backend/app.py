import os
import time
import random
import logging
from flask import Flask, jsonify, request
import psycopg2
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter())
)

app = Flask(__name__)

# Instrument Flask and PostgreSQL
FlaskInstrumentor().instrument_app(app)
Psycopg2Instrumentor().instrument()

tracer = trace.get_tracer(__name__)

def get_db_connection():
    """Get database connection with tracing"""
    return psycopg2.connect(
        host=os.getenv('DATABASE_HOST', 'database'),
        database=os.getenv('DATABASE_NAME', 'demo_db'),
        user=os.getenv('DATABASE_USER', 'demo_user'),
        password=os.getenv('DATABASE_PASSWORD', 'demo_pass'),
        port=os.getenv('DATABASE_PORT', '5432')
    )

def init_database():
    """Initialize database tables"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create products table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                stock INTEGER DEFAULT 0
            )
        ''')
        
        # Insert sample data
        cur.execute('''
            INSERT INTO users (name, email) 
            VALUES 
            ('Alice Johnson', 'alice@example.com'),
            ('Bob Smith', 'bob@example.com')
            ON CONFLICT (email) DO NOTHING
        ''')
        
        cur.execute('''
            INSERT INTO products (name, price, stock) 
            VALUES 
            ('Laptop', 999.99, 10),
            ('Mouse', 29.99, 50),
            ('Keyboard', 79.99, 30)
            ON CONFLICT (id) DO NOTHING
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "backend"})

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users with simulated processing time"""
    with tracer.start_as_current_span("get_users") as span:
        try:
            # Simulate some processing time
            time.sleep(random.uniform(0.1, 0.5))
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT id, name, email, created_at FROM users;')
            users = cur.fetchall()
            cur.close()
            conn.close()
            
            # Format response
            users_list = []
            for user in users:
                users_list.append({
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'created_at': user[3].isoformat() if user[3] else None
                })
            
            span.set_attribute("http.status_code", 200)
            span.set_attribute("users.count", len(users_list))
            return jsonify(users_list)
            
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            span.set_attribute("http.status_code", 500)
            span.record_exception(e)
            return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    with tracer.start_as_current_span("create_user") as span:
        try:
            data = request.get_json()
            if not data or 'name' not in data or 'email' not in data:
                return jsonify({"error": "Name and email are required"}), 400
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;',
                (data['name'], data['email'])
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            span.set_attribute("http.status_code", 201)
            span.set_attribute("user.id", user_id)
            return jsonify({"id": user_id, "name": data['name'], "email": data['email']}), 201
            
        except psycopg2.IntegrityError:
            return jsonify({"error": "Email already exists"}), 400
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            span.set_attribute("http.status_code", 500)
            span.record_exception(e)
            return jsonify({"error": "Internal server error"}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    with tracer.start_as_current_span("get_products") as span:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT id, name, price, stock FROM products;')
            products = cur.fetchall()
            cur.close()
            conn.close()
            
            products_list = []
            for product in products:
                products_list.append({
                    'id': product[0],
                    'name': product[1],
                    'price': float(product[2]),
                    'stock': product[3]
                })
            
            span.set_attribute("http.status_code", 200)
            span.set_attribute("products.count", len(products_list))
            return jsonify(products_list)
            
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            span.set_attribute("http.status_code", 500)
            span.record_exception(e)
            return jsonify({"error": "Internal server error"}), 500

@app.route('/api/order', methods=['POST'])
def create_order():
    """Create a mock order with distributed tracing"""
    with tracer.start_as_current_span("create_order") as span:
        try:
            data = request.get_json()
            if not data or 'product_id' not in data or 'quantity' not in data:
                return jsonify({"error": "Product ID and quantity are required"}), 400
            
            # Simulate order processing
            time.sleep(random.uniform(0.2, 1.0))
            
            # Mock payment processing
            with tracer.start_as_current_span("payment_processing"):
                time.sleep(random.uniform(0.1, 0.3))
                payment_status = "completed"
            
            # Mock inventory update
            with tracer.start_as_current_span("inventory_update"):
                time.sleep(random.uniform(0.1, 0.2))
            
            # Mock email notification
            with tracer.start_as_current_span("email_notification"):
                time.sleep(random.uniform(0.05, 0.1))
            
            order_id = random.randint(1000, 9999)
            
            span.set_attribute("http.status_code", 201)
            span.set_attribute("order.id", order_id)
            span.set_attribute("order.product_id", data['product_id'])
            span.set_attribute("order.quantity", data['quantity'])
            
            return jsonify({
                "order_id": order_id,
                "status": "completed",
                "payment_status": payment_status,
                "message": "Order created successfully"
            }), 201
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            span.set_attribute("http.status_code", 500)
            span.record_exception(e)
            return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=False)
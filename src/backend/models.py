"""
Data models for the OpenTelemetry Demo backend service.

This module defines the data models and database operations
used by the backend service.
"""

import logging
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class User:
    """User model representing application users."""
    
    def __init__(self, id: int, name: str, email: str, created_at: str = None):
        self.id = id
        self.name = name
        self.email = email
        self.created_at = created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            created_at=data.get('created_at')
        )


class Product:
    """Product model representing items for sale."""
    
    def __init__(self, id: int, name: str, price: float, stock: int):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'stock': self.stock
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Create product from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            price=data.get('price'),
            stock=data.get('stock')
        )


class Order:
    """Order model representing customer orders."""
    
    def __init__(self, id: int, user_id: int, product_id: int, quantity: int, 
                 total_price: float, status: str, created_at: str = None):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        self.total_price = total_price
        self.status = status
        self.created_at = created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'total_price': float(self.total_price),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DatabaseManager:
    """Manager for database operations."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.connection_string)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cur.fetchall()
                else:
                    conn.commit()
                    if query.strip().upper().startswith('INSERT'):
                        cur.execute("SELECT LASTVAL()")
                        return [{'id': cur.fetchone()['lastval']}]
                    return []
        except Exception as e:
            conn.rollback()
            logger.error(f"Database query failed: {e}")
            raise
        finally:
            conn.close()
    
    def get_users(self) -> List[User]:
        """Get all users."""
        results = self.execute_query(
            'SELECT id, name, email, created_at FROM users ORDER BY created_at DESC'
        )
        return [User.from_dict(dict(row)) for row in results]
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        results = self.execute_query(
            'SELECT id, name, email, created_at FROM users WHERE id = %s',
            (user_id,)
        )
        if results:
            return User.from_dict(dict(results[0]))
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        results = self.execute_query(
            'SELECT id, name, email, created_at FROM users WHERE email = %s',
            (email,)
        )
        if results:
            return User.from_dict(dict(results[0]))
        return None
    
    def create_user(self, name: str, email: str) -> User:
        """Create a new user."""
        results = self.execute_query(
            'INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id',
            (name, email)
        )
        user_id = results[0]['id']
        return self.get_user_by_id(user_id)
    
    def get_products(self) -> List[Product]:
        """Get all products."""
        results = self.execute_query(
            'SELECT id, name, price, stock FROM products ORDER BY id'
        )
        return [Product.from_dict(dict(row)) for row in results]
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        results = self.execute_query(
            'SELECT id, name, price, stock FROM products WHERE id = %s',
            (product_id,)
        )
        if results:
            return Product.from_dict(dict(results[0]))
        return None
    
    def update_product_stock(self, product_id: int, new_stock: int) -> None:
        """Update product stock."""
        self.execute_query(
            'UPDATE products SET stock = %s WHERE id = %s',
            (new_stock, product_id)
        )
    
    def create_order(self, user_id: int, product_id: int, quantity: int, 
                    total_price: float) -> Order:
        """Create a new order."""
        results = self.execute_query(
            '''INSERT INTO orders (user_id, product_id, quantity, total_price, status) 
               VALUES (%s, %s, %s, %s, 'completed') RETURNING id''',
            (user_id, product_id, quantity, total_price)
        )
        order_id = results[0]['id']
        
        # Get the created order
        results = self.execute_query(
            'SELECT id, user_id, product_id, quantity, total_price, status, created_at FROM orders WHERE id = %s',
            (order_id,)
        )
        if results:
            return Order.from_dict(dict(results[0]))
        return None
    
    def get_orders(self) -> List[Order]:
        """Get all orders."""
        results = self.execute_query(
            'SELECT id, user_id, product_id, quantity, total_price, status, created_at FROM orders ORDER BY created_at DESC'
        )
        return [Order.from_dict(dict(row)) for row in results]
    
    def get_orders_by_user(self, user_id: int) -> List[Order]:
        """Get orders for a specific user."""
        results = self.execute_query(
            'SELECT id, user_id, product_id, quantity, total_price, status, created_at FROM orders WHERE user_id = %s ORDER BY created_at DESC',
            (user_id,)
        )
        return [Order.from_dict(dict(row)) for row in results]


# Database initialization functions
def initialize_database(connection_string: str):
    """Initialize database with required tables and sample data."""
    manager = DatabaseManager(connection_string)
    
    try:
        # Create tables
        manager.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        manager.execute_query('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                stock INTEGER DEFAULT 0
            )
        ''')
        
        manager.execute_query('''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                product_id INTEGER REFERENCES products(id),
                quantity INTEGER NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert sample data
        manager.execute_query('''
            INSERT INTO users (name, email) 
            VALUES 
            ('Alice Johnson', 'alice@example.com'),
            ('Bob Smith', 'bob@example.com'),
            ('Carol Davis', 'carol@example.com')
            ON CONFLICT (email) DO NOTHING
        ''')
        
        manager.execute_query('''
            INSERT INTO products (name, price, stock) 
            VALUES 
            ('Laptop', 999.99, 10),
            ('Mouse', 29.99, 50),
            ('Keyboard', 79.99, 30),
            ('Monitor', 299.99, 15),
            ('Headphones', 149.99, 25)
            ON CONFLICT (id) DO NOTHING
        ''')
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


# Factory function to create database manager
def create_database_manager(host: str = 'localhost', port: int = 5432, 
                          database: str = 'demo_db', user: str = 'demo_user', 
                          password: str = 'demo_pass') -> DatabaseManager:
    """Create a database manager with the given connection parameters."""
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return DatabaseManager(connection_string)
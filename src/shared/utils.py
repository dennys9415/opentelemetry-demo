"""
Shared utilities for the OpenTelemetry Demo application.

This module contains common utility functions used across
multiple services in the application.
"""

import os
import json
import logging
import time
import random
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta


def setup_logging(level: str = 'INFO') -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def get_environment_variable(key: str, default: Any = None) -> Any:
    """
    Get environment variable with optional default.
    
    Args:
        key: Environment variable name
        default: Default value if not found
    
    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)


def generate_trace_metadata(service_name: str) -> Dict[str, Any]:
    """
    Generate metadata for tracing.
    
    Args:
        service_name: Name of the service generating the trace
    
    Returns:
        Dictionary with trace metadata
    """
    return {
        'service.name': service_name,
        'timestamp': datetime.utcnow().isoformat(),
        'environment': get_environment_variable('NODE_ENV', 'development'),
        'version': get_environment_variable('APP_VERSION', '1.0.0')
    }


def simulate_processing_time(min_delay: float = 0.1, max_delay: float = 1.0) -> None:
    """
    Simulate processing time for demo purposes.
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
    """
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


def calculate_throughput(start_time: float, end_time: float, operations: int) -> float:
    """
    Calculate operations per second.
    
    Args:
        start_time: Start timestamp
        end_time: End timestamp
        operations: Number of operations completed
    
    Returns:
        Operations per second
    """
    duration = end_time - start_time
    if duration <= 0:
        return 0.0
    return operations / duration


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f}µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    else:
        return f"{seconds:.2f}s"


def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email is valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_string(input_string: str, max_length: int = 100) -> str:
    """
    Sanitize string input.
    
    Args:
        input_string: String to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = ''.join(char for char in input_string if char.isprintable())
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


class RetryableError(Exception):
    """Exception that can be retried."""
    pass


class NonRetryableError(Exception):
    """Exception that should not be retried."""
    pass


def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exceptions: Exceptions to catch and retry
    
    Returns:
        Function result
    
    Raises:
        Last exception if all retries fail
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                
                if attempt == max_retries:
                    break
                
                # Calculate delay with exponential backoff and jitter
                delay = min(base_delay * (2 ** attempt), max_delay)
                jitter = random.uniform(0, delay * 0.1)
                total_delay = delay + jitter
                
                logging.warning(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {format_duration(total_delay)}"
                )
                time.sleep(total_delay)
        
        raise last_exception
    
    return wrapper


class PerformanceTimer:
    """
    Context manager for measuring execution time.
    """
    
    def __init__(self, operation_name: str = "operation"):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        logging.info(
            f"{self.operation_name} completed in {format_duration(duration)}"
        )
    
    def get_duration(self) -> float:
        """Get the duration of the operation."""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return self.end_time - self.start_time


def generate_sample_data(data_type: str, count: int = 5) -> List[Dict[str, Any]]:
    """
    Generate sample data for testing and demonstration.
    
    Args:
        data_type: Type of data to generate ('users', 'products', 'orders')
        count: Number of items to generate
    
    Returns:
        List of generated data items
    """
    if data_type == 'users':
        return [
            {
                'id': i + 1,
                'name': f'User {i + 1}',
                'email': f'user{i + 1}@example.com',
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
            for i in range(count)
        ]
    
    elif data_type == 'products':
        products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones']
        return [
            {
                'id': i + 1,
                'name': products[i % len(products)],
                'price': round(random.uniform(10.0, 1000.0), 2),
                'stock': random.randint(0, 100)
            }
            for i in range(count)
        ]
    
    elif data_type == 'orders':
        return [
            {
                'id': i + 1,
                'user_id': random.randint(1, 5),
                'product_id': random.randint(1, 5),
                'quantity': random.randint(1, 3),
                'total_price': round(random.uniform(50.0, 500.0), 2),
                'status': random.choice(['pending', 'completed', 'shipped']),
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 7))).isoformat()
            }
            for i in range(count)
        ]
    
    else:
        raise ValueError(f"Unknown data type: {data_type}")


def safe_json_parse(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON string.
    
    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails
    
    Returns:
        Parsed JSON object or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str] = None) -> Dict[str, Any]:
    """
    Mask sensitive data in dictionaries.
    
    Args:
        data: Dictionary containing potentially sensitive data
        sensitive_fields: List of field names to mask
    
    Returns:
        Dictionary with sensitive fields masked
    """
    if sensitive_fields is None:
        sensitive_fields = ['password', 'token', 'secret', 'api_key']
    
    masked_data = data.copy()
    
    for key, value in masked_data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            if isinstance(value, str) and len(value) > 0:
                masked_data[key] = '***MASKED***'
    
    return masked_data


# Configuration management
class Config:
    """
    Configuration management class.
    """
    
    def __init__(self):
        self._config = {
            'app': {
                'name': get_environment_variable('APP_NAME', 'opentelemetry-demo'),
                'version': get_environment_variable('APP_VERSION', '1.0.0'),
                'environment': get_environment_variable('NODE_ENV', 'development')
            },
            'database': {
                'host': get_environment_variable('DATABASE_HOST', 'localhost'),
                'port': int(get_environment_variable('DATABASE_PORT', '5432')),
                'name': get_environment_variable('DATABASE_NAME', 'demo_db'),
                'user': get_environment_variable('DATABASE_USER', 'demo_user'),
                'password': get_environment_variable('DATABASE_PASSWORD', 'demo_pass')
            },
            'opentelemetry': {
                'endpoint': get_environment_variable('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317'),
                'service_name': get_environment_variable('OTEL_SERVICE_NAME', 'demo-service')
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (e.g., 'database.host')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key (e.g., 'database.host')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value


# Global configuration instance
config = Config()
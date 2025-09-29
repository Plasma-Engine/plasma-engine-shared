"""
Common utilities shared across all Plasma Engine services.

Provides reusable functions for:
- Data validation and sanitization
- Date/time handling
- String manipulation
- File operations
- Logging configuration
- Environment management
"""

import os
import re
import json
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
import asyncio
from functools import wraps
import time
import uuid


# Constants
ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
SIMPLE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
URL_REGEX = re.compile(r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/[^?\s]*)?(?:\?[^#\s]*)?(?:#[^\s]*)?$')


class PlasmaEngineError(Exception):
    """Base exception for Plasma Engine services."""
    pass


class ValidationError(PlasmaEngineError):
    """Raised when data validation fails."""
    pass


class ConfigurationError(PlasmaEngineError):
    """Raised when configuration is invalid."""
    pass


def setup_logging(
    service_name: str,
    level: str = "INFO",
    format_str: Optional[str] = None,
    include_correlation_id: bool = True
) -> logging.Logger:
    """
    Setup standardized logging for Plasma Engine services.
    
    Args:
        service_name: Name of the service for log identification
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Custom format string for log messages
        include_correlation_id: Whether to include correlation ID in logs
        
    Returns:
        Configured logger instance
    """
    if not format_str:
        format_str = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            f"[{service_name}] - %(message)s"
        )
        
        if include_correlation_id:
            format_str = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                f"[{service_name}] - [%(correlation_id)s] - %(message)s"
            )
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logger = logging.getLogger(service_name)
    
    # Add correlation ID filter if requested
    if include_correlation_id:
        class CorrelationIdFilter(logging.Filter):
            def filter(self, record):
                if not hasattr(record, 'correlation_id'):
                    record.correlation_id = getattr(
                        asyncio.current_task(), 'correlation_id', 'unknown'
                    ) if asyncio.iscoroutinefunction else 'sync'
                return True
        
        logger.addFilter(CorrelationIdFilter())
    
    return logger


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracking."""
    return f"pe-{int(time.time())}-{secrets.token_hex(8)}"


def generate_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def hash_string(value: str, algorithm: str = "sha256") -> str:
    """
    Hash a string using the specified algorithm.
    
    Args:
        value: String to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
    Returns:
        Hexadecimal hash string
    """
    hasher = hashlib.new(algorithm)
    hasher.update(value.encode('utf-8'))
    return hasher.hexdigest()


def sanitize_string(
    value: str,
    max_length: Optional[int] = None,
    allowed_chars: Optional[str] = None,
    remove_html: bool = False
) -> str:
    """
    Sanitize a string by removing/replacing unwanted characters.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allowed_chars: Regex pattern of allowed characters
        remove_html: Whether to remove HTML tags
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove HTML tags if requested
    if remove_html:
        value = re.sub(r'<[^>]+>', '', value)
    
    # Filter allowed characters
    if allowed_chars:
        value = re.sub(f'[^{allowed_chars}]', '', value)
    
    # Trim to max length
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value.strip()


def validate_email(email: str) -> bool:
    """Validate email address format."""
    return bool(EMAIL_REGEX.match(email))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    return bool(URL_REGEX.match(url))


def validate_uuid(value: str) -> bool:
    """Validate UUID format."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number by removing non-digit characters.
    
    Args:
        phone: Phone number string
        
    Returns:
        Normalized phone number (digits only)
    """
    return re.sub(r'[^\d]', '', phone)


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount with appropriate symbol and precision.
    
    Args:
        amount: Currency amount
        currency: Currency code (USD, EUR, GBP, etc.)
        
    Returns:
        Formatted currency string
    """
    symbols = {
        'USD': '$',
        'EUR': '€', 
        'GBP': '£',
        'JPY': '¥'
    }
    
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def parse_iso_date(date_str: str) -> datetime:
    """
    Parse ISO 8601 date string to datetime object.
    
    Args:
        date_str: ISO 8601 formatted date string
        
    Returns:
        datetime object in UTC
    """
    try:
        # Handle various ISO formats
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        
        return datetime.fromisoformat(date_str).astimezone(timezone.utc)
    except ValueError as e:
        raise ValidationError(f"Invalid date format: {date_str}") from e


def format_iso_date(dt: datetime) -> str:
    """
    Format datetime object to ISO 8601 string.
    
    Args:
        dt: datetime object
        
    Returns:
        ISO 8601 formatted string
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.isoformat()


def days_ago(days: int) -> datetime:
    """Get datetime N days ago."""
    return utc_now() - timedelta(days=days)


def hours_ago(hours: int) -> datetime:
    """Get datetime N hours ago."""
    return utc_now() - timedelta(hours=hours)


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback.
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Safely serialize data to JSON string with fallback.
    
    Args:
        data: Data to serialize
        default: Default JSON string if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(data, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return default


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict, parent_key: str = '', separator: str = '.') -> Dict:
    """
    Flatten nested dictionary with dot notation keys.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        separator: Key separator
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for key, value in d.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
    
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List, key: Optional[Callable] = None) -> List:
    """
    Remove duplicates from list while preserving order.
    
    Args:
        lst: List to process
        key: Optional key function for comparison
        
    Returns:
        List without duplicates
    """
    if key:
        seen = set()
        result = []
        for item in lst:
            k = key(item)
            if k not in seen:
                seen.add(k)
                result.append(item)
        return result
    else:
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]


def safe_cast(value: Any, target_type: type, default: Any = None) -> Any:
    """
    Safely cast value to target type with fallback.
    
    Args:
        value: Value to cast
        target_type: Target type
        default: Default value if casting fails
        
    Returns:
        Casted value or default
    """
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return default


def get_env_var(
    key: str,
    default: Optional[str] = None,
    required: bool = False,
    cast_type: Optional[type] = None
) -> Any:
    """
    Get environment variable with type casting and validation.
    
    Args:
        key: Environment variable key
        default: Default value if not found
        required: Whether the variable is required
        cast_type: Type to cast the value to
        
    Returns:
        Environment variable value
        
    Raises:
        ConfigurationError: If required variable is missing
    """
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ConfigurationError(f"Required environment variable '{key}' not set")
    
    if value is not None and cast_type:
        if cast_type == bool:
            # Handle boolean environment variables
            value = value.lower() in ('true', '1', 'yes', 'on')
        elif cast_type == list:
            # Handle comma-separated lists
            value = [item.strip() for item in value.split(',') if item.strip()]
        else:
            value = safe_cast(value, cast_type, default)
    
    return value


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_file_read(file_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """
    Safely read file content.
    
    Args:
        file_path: Path to file
        encoding: File encoding
        
    Returns:
        File content or None if error
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except (IOError, OSError, UnicodeDecodeError):
        return None


def safe_file_write(
    file_path: Union[str, Path],
    content: str,
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> bool:
    """
    Safely write content to file.
    
    Args:
        file_path: Path to file
        content: Content to write
        encoding: File encoding
        create_dirs: Whether to create parent directories
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return True
    except (IOError, OSError, UnicodeEncodeError):
        return False


def retry_async(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator for retrying async functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts
        backoff: Backoff multiplier
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        raise last_exception
                    
                    await asyncio.sleep(delay * (backoff ** attempt))
            
            raise last_exception
        
        return wrapper
    return decorator


def measure_time(func):
    """
    Decorator to measure function execution time.
    
    Args:
        func: Function to measure
        
    Returns:
        Function wrapper that logs execution time
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            execution_time = (time.time() - start_time) * 1000
            logger = logging.getLogger(func.__module__)
            logger.debug(f"{func.__name__} executed in {execution_time:.2f}ms")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = (time.time() - start_time) * 1000
            logger = logging.getLogger(func.__module__)
            logger.debug(f"{func.__name__} executed in {execution_time:.2f}ms")
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def cache_result(ttl_seconds: int = 300):
    """
    Simple in-memory cache decorator with TTL.
    
    Args:
        ttl_seconds: Time to live in seconds
    """
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check if cached result exists and is still valid
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    return result
                else:
                    del cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator
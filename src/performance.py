"""
Performance optimization layer for instant, powerful results.
Implements caching, connection pooling, and parallel processing.
"""
import hashlib
import json
import time
from functools import lru_cache, wraps
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import asyncio

logger = logging.getLogger(__name__)


class CacheManager:
    """Advanced caching system for instant results"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.ttl = ttl_seconds
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def _hash_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        cache_data = {
            'args': str(args),
            'kwargs': json.dumps(kwargs, sort_keys=True, default=str)
        }
        return hashlib.md5(
            json.dumps(cache_data, sort_keys=True).encode()
        ).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if valid"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    self.hits += 1
                    logger.debug(f"Cache hit: {key}")
                    return value
                else:
                    self.cache.pop(key, None)
                    self.misses += 1
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Store value in cache"""
        with self.lock:
            self.cache[key] = (value, time.time())
            logger.debug(f"Cached: {key}")
    
    def clear(self) -> None:
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate": f"{hit_rate:.1f}%",
            "cached_items": len(self.cache)
        }


# Global cache instances
result_cache = CacheManager(ttl_seconds=3600)
parameter_cache = CacheManager(ttl_seconds=1800)


def cached_result(ttl: int = 3600):
    """Decorator for caching function results"""
    def decorator(func):
        cache = CacheManager(ttl_seconds=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = cache._hash_key(*args, **kwargs)
            cached = cache.get(key)
            
            if cached is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached
            
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        setattr(wrapper, 'cache', cache)
        setattr(wrapper, 'clear_cache', cache.clear)
        setattr(wrapper, 'get_stats', cache.get_stats)
        return wrapper
    
    return decorator


class ParallelProcessor:
    """Process tasks in parallel for maximum speed"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.max_workers = max_workers
    
    def process_parallel(self, tasks: list, func) -> list:
        """
        Execute tasks in parallel
        
        Args:
            tasks: List of task arguments
            func: Function to execute for each task
            
        Returns:
            List of results in order
        """
        futures = {
            self.executor.submit(func, task): idx 
            for idx, task in enumerate(tasks)
        }
        
        results = [None] * len(tasks)
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                logger.error(f"Parallel task failed: {e}")
                results[idx] = None
        
        return results
    
    def shutdown(self) -> None:
        """Shutdown executor"""
        self.executor.shutdown(wait=True)


class ConnectionPool:
    """Database connection pool for instant access"""
    
    def __init__(self, create_connection, pool_size: int = 10):
        self.create_connection = create_connection
        self.pool_size = pool_size
        self.connections = []
        self.available = threading.Semaphore(pool_size)
        self.lock = threading.RLock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        with self.lock:
            try:
                self.connections = [
                    self.create_connection() 
                    for _ in range(self.pool_size)
                ]
                logger.info(f"Connection pool initialized with {self.pool_size} connections")
            except Exception as e:
                logger.error(f"Failed to initialize connection pool: {e}")
    
    def get_connection(self, timeout: float = 5.0):
        """Get connection from pool"""
        acquired = self.available.acquire(timeout=timeout)
        if not acquired:
            raise TimeoutError("No available connections in pool")
        
        with self.lock:
            if self.connections:
                return self.connections.pop()
        return None
    
    def return_connection(self, conn):
        """Return connection to pool"""
        with self.lock:
            if conn and len(self.connections) < self.pool_size:
                self.connections.append(conn)
        self.available.release()


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.lock = threading.RLock()
    
    def record(self, operation: str, duration: float) -> None:
        """Record operation duration"""
        with self.lock:
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for operation"""
        with self.lock:
            if operation not in self.metrics or not self.metrics[operation]:
                return {}
            
            durations = self.metrics[operation]
            return {
                "operation": operation,
                "count": len(durations),
                "avg_ms": sum(durations) / len(durations) * 1000,
                "min_ms": min(durations) * 1000,
                "max_ms": max(durations) * 1000,
                "total_ms": sum(durations) * 1000
            }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get all performance statistics"""
        with self.lock:
            return {
                op: self.get_stats(op) 
                for op in self.metrics.keys()
            }


# Global performance monitor
performance_monitor = PerformanceMonitor()


def time_operation(operation_name: str):
    """Decorator to measure operation time"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                performance_monitor.record(operation_name, duration)
                logger.debug(f"{operation_name} took {duration*1000:.2f}ms")

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                performance_monitor.record(operation_name, duration)
                logger.debug(f"{operation_name} took {duration*1000:.2f}ms")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class FastAsyncQueue:
    """Fast async task queue for instant processing"""
    
    def __init__(self, max_queue_size: int = 1000):
        self.queue = []
        self.max_size = max_queue_size
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
    
    def put(self, item: Any) -> bool:
        """Add item to queue"""
        with self.condition:
            if len(self.queue) >= self.max_size:
                return False
            self.queue.append(item)
            self.condition.notify()
            return True
    
    def get(self, timeout: float = 1.0) -> Optional[Any]:
        """Get item from queue"""
        with self.condition:
            end_time = time.time() + timeout
            while not self.queue:
                remaining = end_time - time.time()
                if remaining <= 0:
                    return None
                self.condition.wait(timeout=remaining)
            
            return self.queue.pop(0) if self.queue else None
    
    def size(self) -> int:
        """Get queue size"""
        with self.lock:
            return len(self.queue)


class ResponseCache:
    """Cache API responses for instant delivery"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self.max_items = 1000
    
    def cache_response(self, key: str, data: Dict, ttl: int = 3600) -> None:
        """Cache a response"""
        with self.lock:
            if len(self.cache) >= self.max_items:
                # Remove oldest entry
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k].get('timestamp', 0)
                )
                self.cache.pop(oldest_key, None)
            
            self.cache[key] = {
                'data': data,
                'timestamp': time.time(),
                'ttl': ttl,
                'expires': time.time() + ttl
            }
    
    def get_response(self, key: str) -> Optional[Dict]:
        """Get cached response if valid"""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            if time.time() > entry['expires']:
                self.cache.pop(key, None)
                return None
            
            return entry['data']
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'total_cached': len(self.cache),
                'max_capacity': self.max_items,
                'utilization': f"{len(self.cache) / self.max_items * 100:.1f}%"
            }


# Global response cache
response_cache = ResponseCache()

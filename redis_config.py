import os
import logging
from types import MethodType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock objects for Redis/Celery to allow app to run without those dependencies
class MockRedisClient:
    """Mock Redis client that logs operations instead of performing them"""
    def __init__(self):
        self.logger = logging.getLogger('mock_redis')
    
    def __getattr__(self, name):
        def mock_method(*args, **kwargs):
            self.logger.debug(f"MockRedis.{name} called with args: {args}, kwargs: {kwargs}")
            return None
        return mock_method

class TaskWrapper:
    """Wrapper for mock task functions with additional methods"""
    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
    
    def __call__(self, *args, **kwargs):
        logger.debug(f"Mock task {self.__name__} called with args: {args}, kwargs: {kwargs}")
        return self.func(*args, **kwargs)
    
    def s(self, *args, **kwargs):
        """Signature method for Celery tasks"""
        logger.debug(f"Mock task signature {self.__name__}.s() called")
        return (self.__name__, args, kwargs)

class MockCeleryApp:
    """Mock Celery app that provides task decorator but doesn't execute tasks"""
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger('mock_celery')
        self.on_after_configure = self.MockEvent()
    
    class MockEvent:
        """Mock event class with connect method"""
        def connect(self, func):
            logger.debug(f"Mock connect for function {func.__name__}")
            return func
    
    def task(self, *args, **kwargs):
        """Task decorator mimicking Celery's task decorator"""
        def decorator(func):
            return TaskWrapper(func)
            
        # Handle both @task and @task()
        if len(args) == 1 and callable(args[0]):
            return decorator(args[0])
        return decorator

# Create mock instances
redis_client = MockRedisClient()
celery_app = MockCeleryApp('household_services')

import time
from functools import wraps


def wait_and_perform(default_condition="presence"):
    def decorator(func):
        @wraps(func)
        def wrapper(self, locator, *args, condition=None, **kwargs):
            used_condition = condition or default_condition
            if isinstance(locator, tuple):
                element = self.wait_for_element(locator, condition=used_condition)
            else:
                element = locator
            return func(self, element, *args, **kwargs)
        return wrapper
    return decorator


def timer(func):
    """计算方法执行时间的装饰器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'Function {func.__name__} execution time: {end - start} seconds')
        return result

    return wrapper
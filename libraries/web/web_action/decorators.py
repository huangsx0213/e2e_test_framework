import time


def timer(func):
    """计算方法执行时间的装饰器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'Function {func.__name__} execution time: {end - start} seconds')
        return result

    return wrapper
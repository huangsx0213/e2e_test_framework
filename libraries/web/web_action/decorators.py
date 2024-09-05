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
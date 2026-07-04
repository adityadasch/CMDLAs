from functools import wraps
import inspect

def requires(*requirements):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) + len(kwargs) == 0:
                print('The function call is empty')
                return None
            
            sign = inspect.signature(func)
            bound = sign.bind(*args, **kwargs)
            bound.apply_defaults()
            
            for req in requirements:
                if bound.arguments.get(req) is None:
                    print(f'{req} is missing')
                    return None
            return func(*bound.args, **bound.kwargs)

        return wrapper
    return decorator

def requires_typed(**requirements):
    '''Checks for presence and type of variables'''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) + len(kwargs) == 0:
                print('The function call is empty')
                return None
            
            sign = inspect.signature(func)
            bound = sign.bind(*args, **kwargs)
            bound.apply_defaults()

            for req, dt in requirements.items():
                if bound.arguments.get(req) is None:
                    print(f'{req} is missing')
                    return None
                if not isinstance(bound.arguments.get(req), dt):
                    dtype = dt.__name__ if not isinstance(dt,(tuple,list,set)) else f"[{','.join([dt_.__name__ for dt_ in dt])}]"
                    print(f'Expected \'{req}\' to be of type(s) {dtype}')
                    return None
            return func(*args, **kwargs)

        return wrapper
    return decorator

def validate(**requirements):
    """variable_name = func()
    Validates if the value provided satisfies func, i.e, func(value)=True"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) + len(kwargs) == 0:
                print('The function call is empty')
            
            sign = inspect.signature(func)
            bound = sign.bind(*args, **kwargs)
            bound.apply_defaults()

            for req, expr in requirements.items():
                if bound.arguments.get(req) is None:
                    print(f'{req} is missing')
                if not expr(bound.arguments.get(req)):
                    print(f'Expected \'{req}\', value={bound.arguments.get
                    (req)} to satisfy filter function')
                    return None
            return func(*args, **kwargs)

        return wrapper
    return decorator
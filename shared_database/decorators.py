from functools import wraps

def run_only_once(f):
    """
    Decorator that memoizes the return value of a function.
    :param f: the function to decorate. Gets called no more than once. Must
        return a not `None` value.
    :return: whatever `f` returns.
    """
    cache = None
    @wraps(f)
    def x():
        nonlocal cache
        if not cache:
            cache = f()
        return cache
    return x

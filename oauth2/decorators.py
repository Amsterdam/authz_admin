""" Some decorators used throughout the code.
"""

from functools import wraps


def memoized(f):
    """
    Decorator that memoizes the return value of a function.

    :param f: the function to decorate. Gets called no more than once.

    :return: whatever `f` returns.

    """
    called = False
    value = None

    @wraps(f)
    def x():
        nonlocal called, value
        if not called:
            value = f()
            called = True
        return value

    return x

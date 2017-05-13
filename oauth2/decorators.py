""" Some decorators used throughout the code.
"""

from functools import update_wrapper


class reify(object):
    """
    Copied from `Pyramid <https://trypyramid.com/>`_

    Use as a method decorator.  It operates almost exactly like the
    Python :class:`@property <property>` decorator, but it puts the
    result of the method it decorates into the instance dict after the
    first call, effectively replacing the function it decorates with an
    instance variable.  It is, in Python parlance, a non-data descriptor.

    """
    def __init__(self, wrapped):
        self.wrapped = wrapped
        update_wrapper(self, wrapped)

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val

"""
A very simple prototypal programming module.

Source: https://bitbucket.org/brankovukelic/pyproto
"""

from copy import copy
from functools import wraps
import types

__all__ = ['Object']


class Object(object):
    """
    Base prototype for prototypal object model in Python.
    
    To create a new object, simply instantiate an Object instance::
    
        >>> my_object = Object()
        
    The newly creted object has a ``__proto__`` attribute, which points to the
    ``Object`` class. Object class itself has no ``__proto__`` attribute.
    
        >>> my_object = Object()
        >>> my_object.__proto__
        <class '__main__.Object'>
        
    The object pointed to by ``__proto__`` is called the prototype. ``Object``
    class itself is called the root prototype.
    Each object has attributes. These attributes can be written and read using
    either dot notation or subscript notation::
    
        >>> my_object = Object()
        >>> my_object.foo = 1
        >>> my_object['foo']
        1
        >>> my_object['bar'] = 2
        >>> my_object.bar
        2
        
    Attributes are resolved first by looking at any attributes defined for the
    instance, and are then looked up in the instance's prototype
    (``__proto__``). If the object's prototype is also a prototype, a chain of
    lookups is started which ends with the root prototype (``Object``). If an
    attribute is not defined on any of the prototypes or the root prototype,
    ``AttributeError`` exception is raised.
    Having ``Object`` as root prototype actually has one very important side
    effect. In essence, we are able to Patch the base object by accessing the
    instance's prototype (provided the instance is directly linked to
    ``Object`` class). Consider this code::
    
        >>> my_object = Object()
        >>> my_other_object = Object()
        >>> my_object.__proto__.foo = 'bar'
        >>> my_other_object.foo
        'bar'
        
    As you can see, we have added the ``foo`` attribute directly to root
    prototype.
    To add methods to an object, you have to first define a function, and then
    assign it to the appropriate attribute::
    
        >>> def my_method(self):
        ...     return 'foo'
        >>> my_object = Object()
        >>> my_object.my_method = my_method
        >>> my_object.my_method()
        'foo'
        
    Objects can be iterated just like normal Python dictionaries::
    
        >>> my_object = Object()
        >>> my_object.foo = 1
        >>> my_object.bar = 2
        >>> for key in my_object:
        ...    print '%s: %s' % (key, my_object[key])
        foo: 1
        bar: 2
        
    Objects also have a few utility methods that makes working with its
    attibutes easier::
    
        >>> my_object = Object()
        >>> my_object.foo = 1
        >>> my_object.bar = 2
        >>> my_object.attrs()
        ['foo', 'bar']
        >>> my_object.items()
        [('foo', 1), ('bar', 2)]
        >>> my_object.dict()
        {'foo': 1, 'bar': 2}
        >>> for attr, val in my_object.items():
        ...     print '%s: %s' % (attr, val)
        foo: 1
        bar: 2
        
    Inheritance is simple. Instantiate an Object instance with an existing
    object as it's first argument::
    
        >>> my_object = Object()
        >>> my_object.foo = 'bar'
        >>> my_other_object = Object(my_object)
        >>> my_other_object.foo
        'bar'
        >>> my_object.bar = 2
        >>> my_other_object.bar
        2
        >>> my_other_object.__proto__ == my_object
        True
        
    We should keep in mind that inheritance is not the same as cloning. While
    the child object has access to all the parent's attributes, it can also
    have its own. Conversely, none of the parent's attributes are child's own,
    so they cannot be iterated over. Here's an example::
    
        >>> my_object = Object()
        >>> my_object.foo = 'bar'
        >>> my_other_object = Object()
        >>> my_other_object.foo
        'bar'
        >>> my_other_object.attrs()
        []
        >>> my_object.attrs()
        ['foo']
    """

    def __init__(self, obj=None):
        self.__proto__ = obj or Object

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, val):
        return self.__setattr__(name, val)

    def __delitem__(self, name):
        return self.__delattr__(name)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        return getattr(self.__proto__, name, None)

    def __setattr__(self, name, value):
        # if name != '__proto__' and hasattr(value, '__call__'):
        if name != '__proto__' and type(value) in (types.FunctionType, types.LambdaType):
            @wraps(value)
            def method(*args, **kwargs):
                return value(self, *args, **kwargs)
            self.__dict__[name] = method
        else:
            self.__dict__[name] = value
        return value

    def hasattr(self, name):
        """
        Overrides `object.hasattr()`.
        """
        return name in self.__dict__

    def __keys__(self):
        return self.__map__().keys()

    def __values__(self):
        return [v for k, v in self.__items__()]

    def __iter__(self):
        return iter(self.__keys__())

    def __map__(self):
        attrs = copy(self.__dict__)
        del attrs['__proto__']
        return attrs

    def __items__(self):
        obj_map = self.__map__()
        return [(k, obj_map[k]) for k in obj_map.keys()]

    def __contains__(self, item):
        return item in self.__keys__()

    attrs = __keys__
    dict = __map__
    items = __items__

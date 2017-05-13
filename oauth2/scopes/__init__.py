"""
Convenient placeholder during developement.

Will be replaced by an actual (database?) backend down the road.

"""

import types
import functools

from .. import config, frozen


# Old stuff from Evert ;-)

_registry = frozen.frozen({
    'default',
    'employee',
    'employee_plus'
})


def get():
    return _registry

# New stuff from Pieter


@functools.lru_cache()
def datasets():
    """
    All datasets defined in the configuration.

    :rtype: tuple(str)
    
    """
    return tuple(config['scopes'].keys())


def implied_scopes():
    result = {}
    for dataset in _SCOPES_PER_DATASET:
        for scopes in _SCOPES_PER_DATASET[dataset]:
            assert isinstance(scopes, tuple)
            implied = []
            for scope in scopes:
                scopename = "%s:%s" % (dataset, scope)
                implied.append(scopename)
                result[scopename] = tuple(implied)
    return types.MappingProxyType(result)



# language=rst
"""
Interface to the datasets and scopes defined in the configuration file.

The configuration file defines a number of *datasets*

"""

import types
import functools

from oauth2 import CONFIG, frozen


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
def all_scopes():
    """
    All scopes defined in the configuration.

    :rtype: frozenset(str)

    """
    retval = CONFIG['datasets']
    for dataset_token in retval:
        dataset = retval[dataset_token]

    return retval


def implied_scopes():
    retval = {}
    for dataset in _SCOPES_PER_DATASET:
        for scopes in _SCOPES_PER_DATASET[dataset]:
            assert isinstance(scopes, tuple)
            implied = []
            for scope in scopes:
                scopename = "%s:%s" % (dataset, scope)
                implied.append(scopename)
                retval[scopename] = tuple(implied)
    return types.MappingProxyType(retval)

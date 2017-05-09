"""
    oauth2.scoperegistry
    ~~~~~~~~~~~~~~~~~~~~

    Convenient placeholder during developement. Will be replaced by an actual
    (database?) backend down the road.
"""
from types import MappingProxyType



# Old stuff from Evert ;-)

_registry = frozenset({
    'default',
    'employee',
    'employee_plus'
})


def get():
    return _registry

_SCOPES_PER_DATASET = {
    'TEST': {
        ('READ', 'WRITE'),
        ('GRANT',)
    }
}
_DATASETS = tuple(_SCOPES_PER_DATASET.keys())


def scopes_per_dataset():
    return _SCOPES_PER_DATASET


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
    return MappingProxyType(result)


def all_scopes():
    return tuple(implied_scopes().keys())


def datasets():
    return set(_SCOPES_PER_DATASET.keys())


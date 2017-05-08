"""
    oauth2.scoperegistry
    ~~~~~~~~~~~~~~~~~~~~

    Convenient placeholder during developement. Will be replaced by an actual
    (database?) backend down the road.
"""

_registry = frozenset({
    'default',
    'employee',
    'employee_plus'
})


def get():
    return _registry

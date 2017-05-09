from collections import Hashable
import logging
from types import MappingProxyType

from . import scoperegistry

_logger = logging.getLogger(__name__)


def _freeze(thing):
    if isinstance(thing, Hashable):
        return thing
    elif isinstance(thing, dict):
        _logger.debug("Freezing dictionary: %s", thing)
        return MappingProxyType({key: _freeze(thing[key]) for key in thing})
    elif isinstance(thing, set):
        _logger.debug("Freezing set: %s", thing)
        return frozenset({_freeze(value) for value in thing})
    elif isinstance(thing, list):
        _logger.debug("Freezing list: %s", thing)
        return tuple([_freeze(value) for value in thing])
    raise TypeError("Can't freeze non-hashable object of type %s: %s" %
                    (type(thing), thing))


_SCOPES_PER_DATASET = _freeze(scoperegistry.scopes_per_dataset())
_DATASETS = _freeze(scoperegistry.datasets())


def scopes_per_dataset():
    return _SCOPES_PER_DATASET


def datasets():
    return _DATASETS

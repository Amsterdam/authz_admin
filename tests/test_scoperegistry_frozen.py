import pytest
from oauth2 import scoperegistry_frozen as scoperegistry
from types import MappingProxyType


def test__freeze():
    frozen = scoperegistry._freeze({'a': [{'b'}]})
    assert isinstance(frozen, MappingProxyType)
    assert tuple(frozen.keys()) == ('a',)
    assert frozen['a'] == (frozenset({'b'}),)

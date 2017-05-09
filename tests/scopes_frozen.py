from scopes import frozen

from types import MappingProxyType


def test__freeze():
    frozen = frozen._freeze({'a': [{'b'}]})
    assert isinstance(frozen, MappingProxyType)
    assert tuple(frozen.keys()) == ('a',)
    assert frozen['a'] == (frozenset({'b'}),)

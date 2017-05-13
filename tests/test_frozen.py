import pytest
from types import MappingProxyType
from oauth2.frozen import frozen

class MutableThing:
    pass


def test_freezing_dict_with_list_of_set():
    f = frozen({'a': [{'b'}]})
    assert isinstance(f, MappingProxyType)
    assert tuple(f.keys()) == ('a',)
    assert isinstance(f['a'], tuple)
    assert len(f['a']) == 1
    assert isinstance(f['a'][0], frozenset)
    assert f['a'][0] == frozenset({'b'})


def test_freezing_mutable_thing():
    with pytest.raises(TypeError):
        frozen(MutableThing())

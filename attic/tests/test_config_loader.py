import pathlib

import pytest

from config_loader import _config_loader


# noinspection PyProtectedMember
def test__load_yaml(tmpdir, monkeypatch):
    configpath = tmpdir.join('testconfig.yml')

    # 1. Invalid yaml file content
    configpath.write('key: [')
    with pytest.raises(_config_loader.ConfigError):
        _config_loader._load_yaml(pathlib.Path(configpath))
    # 2. valid content
    configpath.write('key: value')
    assert _config_loader._load_yaml(pathlib.Path(configpath))['key'] == 'value'


# noinspection PyProtectedMember
def test__interpolate_environment(monkeypatch):
    monkeypatch.setenv('TEST_SUBSTITUTE', 'string')
    # 1. no substitution
    data = {'key': 'value'}
    assert _config_loader._interpolate_environment(data) == data
    data = {'key': True}
    assert _config_loader._interpolate_environment(data) == data
    data = {'key': 1}
    assert _config_loader._interpolate_environment(data) == data
    # 2. simple substitution
    data = {'key': '$TEST_SUBSTITUTE'}
    assert _config_loader._interpolate_environment(data) == {'key': 'string'}
    data = {'key': '${TEST_SUBSTITUTE}s'}
    assert _config_loader._interpolate_environment(data) == {'key': 'strings'}
    data = {'key': '${TEST_SUBSTITUTE-default}s'}
    assert _config_loader._interpolate_environment(data) == {'key': 'strings'}
    data = {'key': '${TEST_SUBSTITUTE:-default}s'}
    assert _config_loader._interpolate_environment(data) == {'key': 'strings'}
    # 3. substitution with defaults
    data = {'key': '${GHOST:-default}'}
    assert _config_loader._interpolate_environment(data) == {'key': 'default'}
    data = {'key': '${GHOST:-/non:-alphanumeric}'}
    assert _config_loader._interpolate_environment(data) == {'key': '/non:-alphanumeric'}
    # 4. missing substitute
    data = {'key': '$GHOST'}
    with pytest.raises(_config_loader.ConfigError):
        _config_loader._interpolate_environment(data)
    # 5. escaped values
    data = {'key': '$$ESC'}
    assert _config_loader._interpolate_environment(data) == {'key': '$ESC'}
    # 6. invalid substitution
    data = {'key': '${'}
    with pytest.raises(_config_loader.ConfigError):
        _config_loader._interpolate_environment(data)
    data = {'key': '${ TEST_SUBSTITUTE}'}
    with pytest.raises(_config_loader.ConfigError):
        _config_loader._interpolate_environment(data)
    data = {'key': '${TEST_SUBSTITUTE }'}
    with pytest.raises(_config_loader.ConfigError):
        _config_loader._interpolate_environment(data)
    data = {'key': '${ }'}
    with pytest.raises(_config_loader.ConfigError):
        _config_loader._interpolate_environment(data)
    # 7. nested substitution
    data = {'key': ['$TEST_SUBSTITUTE']}
    assert _config_loader._interpolate_environment(data) == {'key': ['string']}
    data = {'key': {'test': '$TEST_SUBSTITUTE'}}
    assert _config_loader._interpolate_environment(data) == {'key': {'test': 'string'}}
    data = {'key': [{'test': '$TEST_SUBSTITUTE'}]}
    assert _config_loader._interpolate_environment(data) == {'key': [{'test': 'string'}]}


# noinspection PyProtectedMember
def test__validate(tmpdir):
    invalid_schema = "}"
    valid_schema = """
    {
      "$schema": "http://json-schema.org/draft-04/schema#",
      "type": "object",
      "required": ["test"],
      "properties": {
        "test": {"type": "string"}
      }
    }
    """

    schemapath = tmpdir.join('testschema.json')

    # 1. missing schema
    with pytest.raises(FileNotFoundError):
        # noinspection PyProtectedMember
        _config_loader._validate({}, pathlib.Path(schemapath))
    # 2. invalid schema
    schemapath.write(invalid_schema)
    with pytest.raises(_config_loader.ConfigError):
        # noinspection PyProtectedMember
        _config_loader._validate({}, pathlib.Path(schemapath))
    # 3. invalid data
    schemapath.write(valid_schema)
    with pytest.raises(_config_loader.ConfigError):
        # noinspection PyProtectedMember
        _config_loader._validate({}, pathlib.Path(schemapath))
    # 4. valid everything
    # noinspection PyProtectedMember
    _config_loader._validate({'test': 'string'}, pathlib.Path(schemapath))

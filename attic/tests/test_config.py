import pathlib

import pytest

from oauth2 import config
import config_loader


def test_get(tmpdir, monkeypatch):
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
    valid_yaml = "test: ${DUMMY-default}\noptional: abcd"
    invalid_yaml = "optional: abcd"
    expected = {'test': 'default', 'optional': 'abcd'}
    tmpdir.join('config1.yml').write(invalid_yaml)
    tmpdir.join('config2.yml').write(valid_yaml)
    schema_file = tmpdir.join('schema.json')
    schema_file.write(valid_schema)
    monkeypatch.setattr(config, 'CONFIG_SCHEMA_V1_PATH', pathlib.Path(schema_file))
    monkeypatch.setattr(config, 'DEFAULT_CONFIG_PATHS', [
        pathlib.Path(tmpdir) / 'non_existing.yml',
        pathlib.Path(tmpdir) / 'config2.yml'
    ])
    monkeypatch.setenv('CONFIG_PATH', str(tmpdir.join('config1.yml')))
    with pytest.raises(config_loader.ConfigError):
        config.get()
    monkeypatch.delenv('CONFIG_PATH')
    assert config.get() == expected

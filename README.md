## Config Parser

A simple config parser to read and parse configuration from a given file.

It provides a method `load_config` to read and parse configuration from a given file.

### Usage:

```python
>>> CONFIG = load_config("/path/to/settings.conf", ["override1", "override2"]))

>>> CONFIG.group_name.setting # returns value of `setting` in `group_name` group.

"value"

>>> CONFIG.group_name # returns a dict with all settings for `group_name` group.

{"setting1": "value1", "setting2": "value2"}

>>> CONFIG.non_existent # returns None when you ask for non-existent key.

None
```

### Tests

The config parser uses `unittest` module for unit testing the features. It has a suite of unit tests in `test_config_parser.py`.

You can run the tests by running:

```
make test
```

alternatively, you can use unittest directly to run the tests:

```
python -m unittest discover
```
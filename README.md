## Config Parser

A simple config parser which provides a method `load_config` to
read and parse configuration from a given file.

### Usage:

```python
>>> CONFIG = load_config("/path/to/settings.conf", ["override1", "override2"]))

>>> CONFIG.groupname.setting # returns value of setting in groupname.

"value"

>>> CONFIG.groupname # returns a dict with all settings for groupname.

{"setting1": "value1", "setting2": "value2"}
```

### Tests

The config parser uses `unittest` module for unit testing the features. It has a good suite of unit tests in `test_config_parser.py`.

You can run the tests by running:

```
make test
```

alternatively, you can use unittest directly to run the tests:

```
python -m unittest discover
```
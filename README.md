# Config Parser

A simple config parser to read and parse configuration from a given file.

It provides a method `load_config` to read and parse configuration from a given file.

## Usage:

```python
>>> CONFIG = load_config("/path/to/settings.conf", ["override1", "override2"]))

>>> CONFIG.group_name.setting # returns value of `setting` in `group_name` group.

"value"

>>> CONFIG.group_name # returns a dict with all settings for `group_name` group.

{"setting1": "value1", "setting2": "value2"}

>>> CONFIG.non_existent # returns None when you ask for non-existent key.

None
```

## Tests

The config parser uses `unittest` module for unit testing the features. It has a suite of unit tests in `test_config_parser.py`.

You can run the tests by running:

```
make test
```

alternatively, you can use unittest directly to run the tests:

```
python -m unittest discover
```

## Design Decisions

1. To handle very large configurations files, we are reading the file line by line which means we will never hold the entire file in memory.

2. We have used compiled regular expressions because it's more efficient to reuse them as they are going to be used several times in a run of the module.

3. One of the biggest design decision is to use `AttributeDict` which is extended from Python dict. In order to make sure we can access dictionary keys using attribute access method (config.something), we have overridden `__getattr__` method. Similarly, in order to make sure we can handle accessing non-existent keys using dictionary key access method (config["something"]), we have overridden `__getitem__` method. This data structure will ensure that we will not crash or exit the program while accessing any kind of key. A default value `None` is returned when a key doesn't exist.

4. When we read a (setting_name, value) pair, we have assumed that the `setting_name` will always be parsed as a string. However, `value` can be parsed as any of the primitives (int, float, boolean, string) or some of the non-primitives (list). We have assumed that a `value` can't be parsed as a dict or tuple.

5. If the file isn't a valid one, we throw custom exceptions using a verbose message explaining the error. We raise `DuplicateGroupError` when we find a duplicate group entry in our configuration file. We raise `MissingGroupError` when we find a settings line before any line containing a group. We raise `InvalidLineError` when we don't know how to parse any line in the configuration file.

## Further Improvements

1. Handle errors better to suit the client needs. We can extend our config parser to be a ConfigParser class which can be used by different clients. This way different clients can decide how they want to handle the error handling by using certain flags. For example:

    a. For a configuration file which has a line with unknown contents, we may choose to ignore that line as long as the configuration is valid otherwise. We can use flags like `ignore_invalid_lines`, etc.

    b. We may also choose to ignore or override the settings when a duplicate group is found. We can use flags like `override_duplicate_group` or `ignore_duplicate_group`.

    c. On a similar note, we can choose to ignore all settings before a valid group name.

2. Add benchmarks to measure the performance of config parser for different sizes of configuration files. We can use `timeit` module for writing benchmarks.

3. Extend the parsing logic to parse setting value as `dict` or `tuple` as well.

4. Parsing logic for list can be extended to parse a `list` from [value1, value2] format. Right now, the list can only be parsed from comma-separated values.

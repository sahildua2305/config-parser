# Run with: `python -m unittest discover`

import unittest
import config_parser


class TestGetInt(unittest.TestCase):
    """Class to test `get_int` method."""

    def test_valid_int_value(self):
        s = "1"
        self.assertEqual(config_parser.get_int(s), 1)

    def test_invalid_int_float_value(self):
        s = "1.00"
        self.assertIsNone(config_parser.get_int(s))

    def test_invalid_int_value(self):
        s = "as"
        self.assertIsNone(config_parser.get_int(s))


class TestGetFloat(unittest.TestCase):
    """Class to test `get_float` method."""

    def test_valid_float_value(self):
        s = "1.00"
        self.assertEqual(config_parser.get_float(s), 1.00)

    def test_valid_float_int_value(self):
        s = "1"
        self.assertEqual(config_parser.get_float(s), 1)

    def test_invalid_float_value(self):
        s = "1.2s"
        self.assertIsNone(config_parser.get_float(s))


class TestGetBoolean(unittest.TestCase):
    """Class to test `get_boolean` method."""

    def test_valid_true_boolean_value(self):
        s = "true"
        self.assertTrue(config_parser.get_boolean(s))

    def test_valid_zero_boolean_value(self):
        s = "0"
        self.assertFalse(config_parser.get_boolean(s))

    def test_valid_no_boolean_value(self):
        s = "no"
        self.assertFalse(config_parser.get_boolean(s))

    def test_invalid_boolean_value_string(self):
        s = "what"
        self.assertIsNone(config_parser.get_boolean(s))

    def test_invalid_boolean_value_list(self):
        s = "no,yes"
        self.assertIsNone(config_parser.get_boolean(s))


class TestGetList(unittest.TestCase):
    """Class to test `get_list` method."""

    def test_valid_list_without_space(self):
        s = "array,of,values"
        self.assertListEqual(
            config_parser.get_list(s),
            ["array", "of", "values"]
        )

    def test_valid_list_with_space(self):
        s = "array, of, values"
        self.assertListEqual(
            config_parser.get_list(s),
            ["array", "of", "values"]
        )

    def test_valid_list_of_booleans(self):
        s = "1,true, no"
        self.assertListEqual(
            config_parser.get_list(s),
            [True, True, False]
        )

    def test_valid_list_of_int_floats(self):
        s = "1.0, 2, 3.3"
        self.assertListEqual(
            config_parser.get_list(s),
            [1.0, 2, 3.3]
        )

    def test_invalid_list_string(self):
        s = "word"
        self.assertIsNone(config_parser.get_list(s))

class TestTrimComment(unittest.TestCase):
    """Class to test `trim_comment` method."""

    def test_trim_inline_comment(self):
        line = "path = /tmp/; comment"
        self.assertEqual(config_parser.trim_comment(line), "path = /tmp/")

    def test_trim_full_line_comment(self):
        line = "; comment line"
        self.assertEqual(config_parser.trim_comment(line), "")

    def test_trim_full_line_comment_with_leading_spaces(self):
        line = "                ;      comment line"
        self.assertEqual(config_parser.trim_comment(line), "")


class TestParseGroupName(unittest.TestCase):
    """Class to test `parse_group_name` method."""

    def test_valid_group_name(self):
        line = "[http]"
        self.assertEqual(config_parser.parse_group_name(line), "http")

    def test_invalid_group_name(self):
        line = "http"
        self.assertIsNone(config_parser.parse_group_name(line))

    def test_empty_group_name(self):
        line = "[]"
        self.assertIsNone(config_parser.parse_group_name(line))


class TestParseSettingValue(unittest.TestCase):
    """Class to test `parse_setting_value` method."""

    def test_invalid_setting_value(self):
        line = "[group]"
        self.assertTupleEqual(
            config_parser.parse_setting_value(line),
            (None, None)
        )

    def test_valid_setting_value_with_space(self):
        line = "path = /tmp/"
        self.assertTupleEqual(
            config_parser.parse_setting_value(line),
            ("path", "/tmp/")
        )

    def test_valid_setting_value_without_space(self):
        line = "path=/tmp/"
        self.assertTupleEqual(
            config_parser.parse_setting_value(line),
            ("path", "/tmp/")
        )

    def test_empty_string(self):
        line = "=1"
        self.assertTupleEqual(
            config_parser.parse_setting_value(line),
            (None, None)
        )
    
    def test_valid_setting_value_with_override(self):
        line = "path<staging> = /srv/uploads/"
        self.assertTupleEqual(
            config_parser.parse_setting_value(line),
            ("path<staging>", "/srv/uploads/")
        )

    def test_valid_setting_int_value(self):
        line = "basic_size_limit = 26214400"
        self.assertTupleEqual(
            config_parser.parse_setting_value(line),
            ("basic_size_limit", 26214400)
        )

    def test_valid_setting_boolean_value(self):
        line = "enabled = no"
        self.assertTupleEqual(
            config_parser.parse_setting_value(line),
            ("enabled", False)
        )

    def test_valid_list_value_without_space(self):
        line = "params = array,of,values"
        self.assertTupleEqual(
            config_parser.parse_setting_value(line),
            ("params", ["array", "of", "values"])
        )

    def test_valid_list_value_with_space(self):
        line = "params = array, of, values"
        self.assertTupleEqual(
            config_parser.parse_setting_value(line),
            ("params", ["array", "of", "values"])
        )


class TestParseSettingOverrideValue(unittest.TestCase):
    """Class to test `parse_setting_override_value` method."""

    def test_valid_setting_override_value(self):
        line = "path<production> = /srv/var/tmp/"
        self.assertTupleEqual(
            config_parser.parse_setting_override_value(line),
            ("path", "production", "/srv/var/tmp/")
        )

    def test_invalid_setting_override_value(self):
        line = "path = /srv/var/tmp/"
        self.assertTupleEqual(
            config_parser.parse_setting_override_value(line),
            (None, None, None)
        )


class TestLoadConfig(unittest.TestCase):
    """Class to test `load_config` method."""

    def test_valid_small_config_without_overrides(self):
        CONFIG = config_parser.load_config(
            "./test_config_data/config_small.conf")

        # Check for type of CONFIG
        self.assertIsNotNone(CONFIG)
        self.assertIsInstance(CONFIG, dict)

        # Check for invalid keys
        self.assertIsNone(CONFIG.something)
        self.assertIsNone(CONFIG.http.something)

        # Check for some valid settings
        self.assertEqual(CONFIG.common.student_size_limit, 52428800)
        self.assertListEqual(CONFIG.http.params, ["array", "of", "values"])
        self.assertEqual(CONFIG.ftp.name, "hello there, ftp uploading")
        self.assertDictEqual(
            CONFIG.ftp,
            {
                'path': '/tmp/',
                'enabled': False,
                'name': 'hello there, ftp uploading'
            }
        )

    def test_valid_small_config_with_overrides(self):
        CONFIG = config_parser.load_config(
            "./test_config_data/config_small.conf", overrides=["production", "ubuntu"])

        # Check for type of CONFIG
        self.assertIsNotNone(CONFIG)
        self.assertIsInstance(CONFIG, dict)

        # Check for invalid settings
        self.assertIsNone(CONFIG.something)
        self.assertIsNone(CONFIG["something"])
        self.assertIsNone(CONFIG.http.something)

        # Check for some valid settings
        self.assertEqual(CONFIG.common.student_size_limit, 52428800)
        self.assertEqual(CONFIG.common["student_size_limit"], 52428800)
        self.assertListEqual(CONFIG.http.params, ["array", "of", "values"])
        self.assertEqual(CONFIG.ftp.name, "hello there, ftp uploading")
        self.assertDictEqual(
            CONFIG.ftp,
            {
                'path': '/etc/var/uploads',
                'enabled': False,
                'name': 'hello there, ftp uploading'
            }
        )

        # Check for some settings with overrides
        self.assertEqual(CONFIG.ftp.path, "/etc/var/uploads")
        self.assertEqual(CONFIG.ftp["path"], "/etc/var/uploads")

    def test_invalid_config_with_missing_group(self):
        with self.assertRaises(config_parser.MissingGroupError):
            ___ = config_parser.load_config("./test_config_data/config_missing_group.conf")

    def test_invalid_config_with_duplicate_group(self):
        with self.assertRaises(config_parser.DuplicateGroupError):
            __ = config_parser.load_config("./test_config_data/config_duplicate_group.conf")

    def test_invalid_config_with_garbage_line(self):
        with self.assertRaises(config_parser.InvalidLineError):
            __ = config_parser.load_config("./test_config_data/config_garbage_line.conf")
    
    def test_invalid_config_missing_file(self):
        with self.assertRaises(IOError):
            __ = config_parser.load_config("./test_config_data/config_missing_file.conf")


if __name__ == "__main__":
    unittest.main()

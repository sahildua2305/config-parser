"""
Config Parser 
"""

import re

# Compiled regular expression for matching group name.
_GROUP_TMPL = r"""
    \[      # [
    (.+)   # group
    \]      # ]
    """
GROUP_CRE = re.compile(_GROUP_TMPL, re.VERBOSE)

# Compiled regular expression for matching (setting, value) pair.
_SETTING_TMPL = r"""
    ^(.+)    # setting
    \s?       # optional space
    =         # =
    \s?       # optional space
    (.+)$    # value
    """
SETTING_CRE = re.compile(_SETTING_TMPL, re.VERBOSE)

# Compiled regular expression for matching setting override.
_SETTING_OVERRIDE_TMPL = r"""
    ^(.+)      # setting
    <(.+)>     # <override>
    \s?         # optional space
    =           # =
    \s?         # optional space
    (.+)$      # value
    """
SETTING_OVERRIDE_CRE = re.compile(_SETTING_OVERRIDE_TMPL, re.VERBOSE)

# Compiled regular expression for matching comments.
_COMMENT_TMPL = r"""
    ([;]+)    # ;
    .*$       # comment text
    """
COMMENT_CRE = re.compile(_COMMENT_TMPL, re.VERBOSE)

# Compiled regular expression for matching quoted strings.
_QUOTED_STRING_TMPL = r"""
    (\"|\')
    (.+)
    (\"|\')
    """
QUOTED_STRING_CRE = re.compile(_QUOTED_STRING_TMPL, re.VERBOSE)

# Permitted boolean values for this config parser.
PERMITTED_BOOLEAN_VALUES = {
    "yes": True, "no": False,
    "true": True, "false": False,
    "1": True, "0": False,
}


class Error(Exception):
    """Base class for custom exceptions.
    """

    def __init__(self, message):
        super(Error, self).__init__(message)


class DuplicateGroupError(Error):
    """Custom error to return when a duplicate group is found
    while parsing the configuration file.
    """

    def __init__(self, group, file_path, line_number):
        message = "Duplicate group '" + str(group) + "' found at line " + \
            str(line_number) + " while parsing file at " + str(file_path)
        super(DuplicateGroupError, self).__init__(message)


class InvalidLineError(Error):
    """Custom error to return when a line can't be parsed
    according to any of the known patterns.
    """

    def __init__(self, file_path, line_number):
        message = "Unable to parse line " + \
            str(line_number) + " while parsing file at " + str(file_path)
        super(InvalidLineError, self).__init__(message)


class MissingGroupError(Error):
    """Custom error to return when the file doesn't start
    with a group. This means we don't know how to handle the
    settings in the beginning of the file.
    """

    def __init__(self, file_path, line_number):
        message = "Unable to find a group at line " + \
            str(line_number) + " while parsing file at " + str(file_path)
        super(MissingGroupError, self).__init__(message)


class AttributeDict(dict):
    """AttributeDict is a wrapper around python dict
    which makes it possible to access dictionary keys
    as attributes.

    For example:
    config["one"]["two"] can be accessed as: config.one.two

    We achieve this feature by overriding __getattr__ method
    to return None when the key doesn't exist.

    We have also overridden __getitem__ method in order to
    support returning None for non-existent keys when user is
    trying to access the non-existent key as config["key"].
    """

    def __init__(self):
        super(AttributeDict, self).__init__()
    
    def __getattr__(self, key):
        return self.get(key, None)

    def __getitem__(self, key):
        return self.get(key, None)


def is_empty_line(line):
    """Function to check if the given line is whitespace only.

    Returns a boolean.
    """
    if line and line.strip():
        return False
    return True


def parse_group_name(line):
    """Function to parse the group name from the following
    pattern:

    [group]

    Returns a string.
    """
    match = GROUP_CRE.match(line)
    if match is not None and len(match.groups()) == 1:
        return match.group(1).strip()
    return None


def parse_setting_value(line):
    """Function to parse the setting value from the following
    pattern:

    setting = value

    Returns a tuple of (setting, value).
    """
    match = SETTING_CRE.match(line)
    if match is not None and len(match.groups()) == 2:
        return (
            match.group(1).strip(),
            parse_value(match.group(2).strip())
        )
    return None, None


def parse_setting_override_value(line):
    """Function to parse the setting override value from the following
    pattern:

    setting<override> = value

    Returns a tuple of (setting, override, value).
    """
    match = SETTING_OVERRIDE_CRE.match(line)
    if match is not None and len(match.groups()) == 3:
        return (
            match.group(1).strip(),
            match.group(2).strip(),
            parse_value(match.group(3).strip())
        )
    return (None, None, None)


def trim_comment(line):
    """Function to trim off the comment starting with ';'
    character from the given line. A typical comment looks
    like this:

    ; this is a comment
    or
    [group]; this is a comment

    Returns the line after trimming the comment, if any.
    """
    return COMMENT_CRE.sub(repl="", string=line).strip()


def is_number(s):
    """Function to check if the string is a number.

    Returns True if string is a number.
    """
    return s.replace('.', '', 1).isdigit()


def get_int(s):
    """Function to return int value from the string, if
    it's a valid one.
    """
    try:
        return int(s)
    except ValueError:
        return None


def get_float(s):
    """Function to return float value from the string, if
    it's a valid one.
    """
    try:
        return float(s)
    except ValueError:
        return None


def get_boolean(s):
    """Function to return boolean value from the string, if
    it's a valid one according to the permitted boolean values.
    """
    if s.lower() in PERMITTED_BOOLEAN_VALUES:
        return PERMITTED_BOOLEAN_VALUES[s]
    return None


def get_list(s):
    """Function to return list of strings, if the given string
    is a comma separated list of values.
    """
    list_value = s.split(",")
    if len(list_value) > 1:
        return [parse_value(element.strip()) for element in list_value]
    return None


def get_quoted_string(s):
    """Function to return quoted string.
    """
    quoted_string = QUOTED_STRING_CRE.match(s)
    if quoted_string is not None and len(quoted_string.groups()) == 3:
        return quoted_string.group(2).strip()
    return None


def parse_value(value):
    """Function to parse a setting value.
    The string parsed can be any of the following types:

    int
    boolean
    array of comma separated values
    string
    string wrapped in quotes (single and double)
    """
    # Check for quoted string
    quoted_string = get_quoted_string(value)
    if quoted_string is not None:
        return quoted_string

    # If the value looks like a number, check for both
    # int and float in greedy fashion.
    if is_number(value):
        # Check for integer
        integer_value = get_int(value)
        if integer_value is not None:
            return integer_value

        # Check for float
        float_value = get_float(value)
        if float_value is not None:
            return float_value

    # Check for boolean
    boolean_value = get_boolean(value)
    if boolean_value is not None:
        return boolean_value

    # Check for list of values
    list_value = get_list(value)
    if list_value is not None:
        return list_value

    return value


def load_config(file_path, overrides=None):
    """Main function to parse a configuration file from a given
    file path and a list of overrides.
    """
    # Initialize config as AttributeDict.
    config = AttributeDict()
    # Keeping track of line number here to be used for error reporting.
    line_number = 0
    # Keeping track of current group here to be used to save setting, value pairs.
    curr_group = None

    # Convert overrides into a set so that we can easily look up
    # if a given override is enabled or not.
    enabled_overrides = set()
    if overrides is not None:
        enabled_overrides = set(overrides)

    # Open the given file and read it line by line.
    # This is a handy way to handle reading big files where we
    # don't need to keep more than one line in memory at one time.
    with open(file_path) as file:
        for line in file:
            line_number += 1

            # Trim off the inline comment from end of the line.
            line = trim_comment(line)

            # Skip the empty lines.
            # Here, we are also covering the line which contains a comment
            # only. For such a line, we will be left with empty string after
            # trimming the comment on last line.
            if is_empty_line(line):
                continue

            # Try to parse group name from current line.
            new_group = parse_group_name(line)
            if new_group is not None:
                # If we have seen this group before, raise exception.
                #
                # IDEA: We have two alternate options here.
                # - we can overwrite the group settings if we find it again.
                # - we can ignore if a group is found as a duplicate.
                if new_group in config:
                    raise DuplicateGroupError(new_group, file_path, line_number)

                # Initialize a new AttributeDict since this is a new group.
                config[new_group] = AttributeDict()
                # Update current group to which we will be saving all next settings.
                curr_group = new_group
                continue

            # Try to parse (setting, value) pair from current line.
            original_setting, value = parse_setting_value(line)
            if original_setting is not None and value is not None:
                # If we found a settings line, however, there was no group
                # found before while parsing this file, raise exception.
                #
                # IDEA: This scenario is up to us how we want to handle it.
                # Alternatively, we could also simply ignore all settings
                # until we find a group in the file.
                if curr_group is None:
                    raise MissingGroupError(file_path, line_number)

                # Try to parse according to setting override pattern.
                setting_without_override, override, __ = parse_setting_override_value(line)
                if override is None: # no override found
                    config[curr_group][original_setting] = value
                elif override in enabled_overrides: # an enabled override found
                    config[curr_group][setting_without_override] = value
                continue

            # If we reach this point, that means we weren't able to parse
            # the current line in any of the known ways.
            #
            # IDEA: This decision is up to us how we want to handle it.
            # Alternatively, we could also simply ignore any line that we don't
            # identify and keep on reading the file further.
            raise InvalidLineError(file_path, line_number)

    return config

if __name__ == "__main__":
    CONFIG = load_config("./config_data/sample_config.conf", overrides=['ubuntu', 'production'])
    print CONFIG

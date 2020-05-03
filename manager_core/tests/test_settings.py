import json
import pytest
from manager_core.Settings import Settings


def test_update_config(create_test_config_file):
    path = create_test_config_file
    test_dict = {'a': 1, 'b': 2, 'c': 3, }
    settings = Settings([], [])
    settings.location = path
    settings.cached_config = test_dict
    settings.update_config()

    file_dict = {}
    with open(path) as f:
        file_dict = json.load(f)

    assert file_dict == test_dict


def test_is_defined(settings_fixture):
    settings = settings_fixture

    # is setting defined as optional or required
    assert settings._is_setting_defined("ROOT_DIR_NAME") is True

    # is not required or optional
    assert settings._is_setting_defined("NOT_NOT_DEFINED") is False


def test_is_specified(settings_fixture):
    settings = settings_fixture

    # setting not specified
    assert settings._is_in_file("ROOT_DIR_NAME") is True

    # setting is specified
    assert settings._is_in_file("SOME RANDOM THING") is False


def test_all_settings(settings_fixture):
    settings = settings_fixture
    settings.required_settings = ["a", "b"]
    settings.optional_settings = [("c", True), ("d", False)]
    assert settings._all_setting_names() == ["a", "b", "c", "d"]


def test_get_optional_default(settings_fixture):
    settings = settings_fixture

    list_opt_value = [0, 1, 2]
    assert settings._get_optional_default("TESTING") is False
    assert settings._get_optional_default("IS_BUILD") is False
    assert settings._get_optional_default("LIST_OPT") == list_opt_value


def test_is_optional(settings_fixture):
    settings = settings_fixture

    assert settings._is_optional("TESTING") is True
    assert settings._is_optional("ROOT_DIR_NAME") is False
    assert settings._is_optional("NON EXISTENT") is False


def test_get_parser(settings_fixture):
    settings = settings_fixture

    def some_func():
        return "I do nothing"

    settings.parsers[some_func.__name__] = some_func
    assert settings._get_parser('some_func') == some_func


def test_add_parser(settings_fixture):
    settings = settings_fixture

    @settings.add_parser
    def ROOT_DIR_NAME(setting_value):
        return f"Parsed{setting_value}"

    parser_func = settings._get_parser('ROOT_DIR_NAME')
    assert parser_func('ROOT_DIR_NAME') == ROOT_DIR_NAME('ROOT_DIR_NAME')


def test_update_setting(settings_fixture):
    settings = settings_fixture

    # Setting exists
    settings.update_setting("ROOT_DIR_NAME", "Some name")
    assert settings.get_attr("ROOT_DIR_NAME") == "Some name"

    # Doesn't reload the file values
    in_memory_dict = settings.cached_config
    settings.reload_cache()
    assert settings.cached_config != in_memory_dict

    # Setting does not exist
    with pytest.raises(LookupError) as e:
        settings.update_setting("NON EXISTENT SETTING", "Some value")


def test_update_setting_reload(settings_fixture):
    settings = settings_fixture

    prev_cache = settings.cached_config.copy()

    # Reloads the file values
    settings.update_setting_reload("ROOT_DIR_NAME", "Some name")
    assert settings.cached_config != prev_cache


def test_get_attr(settings_fixture):
    settings = settings_fixture
    settings.update_setting_reload("TESTING", True)

    # If is an optional setting but is not in the file
    assert settings.get_attr("IS_BUILD") is False

    # If is an optional setting but is in the file
    testing_setting = settings.get_attr('TESTING')
    assert testing_setting != settings._get_optional_default('TESTING')
    assert testing_setting is True

    # Is a required setting and in the file
    assert settings.get_attr("ROOT_DIR_NAME") == "CurbTheScreen"

    # Is a setting with a required parser associated
    @settings.add_parser
    def ROOT_DIR_NAME(setting_value):
        return "dir name was parsed"

    assert settings.get_attr("ROOT_DIR_NAME") == "dir name was parsed"

    # Is a setting with an optional parser associated
    @settings.add_parser
    def TESTING(setting_value):
        return f"testing parsed"

    assert settings.get_attr("TESTING") == "testing parsed"

    # Is not a defined setting
    with pytest.raises(LookupError) as e:
        settings.get_attr("NOT A SETTING")

from unittest.mock import patch
import pytest
import manager_core.SettingsParser as SettingsParser
import manager_core.Settings
from manager_core.CurbTheScreen import DataManager, TrackedProgram, ProgramStates
import os

base_loc = manager_core.Settings.get_base_loc(manager_core.Settings.root_dir_name)
SettingsParser.settings.location = base_loc / 'manager_core' / 'tests' / 'test_resources' / 'test_config.json'
SettingsParser.settings.reload_cache()
SettingsParser.settings.update_setting("TESTING", True)


@pytest.fixture(scope="session")
def create_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("db_resources")
    DataManager.init_db(path)
    return DataManager


@pytest.fixture(scope="function")
def reset_db(create_db):
    db = create_db
    db.reset_db()


@pytest.fixture(scope="session")
def create_test_config_file(tmp_path_factory):
    path = tmp_path_factory.mktemp("config_resources")
    path = path / "temp_config.json"
    with path.open(mode="w+") as f:
        pass
    return path


@pytest.fixture(scope="function")
def settings_fixture(create_test_config_file):
    required_keys = [
        'ROOT_DIR_NAME',
        'LOOP_TIME',
        'TRACKED_PROGRAMS',
    ]

    # The setting name and the default value
    optional_keys = [
        ('TESTING', False),
        ('IS_BUILD', False),
        ('LIST_OPT', [0, 1, 2])
    ]

    store_settings = {
        "ROOT_DIR_NAME": "CurbTheScreen",
        "LOOP_TIME": 1,
        "TRACKED_PROGRAMS": {
            "Calculator": 10,
            "Discord": 10,
            "Chrome": 20
        },
        "TESTING": False,
        "NOT_DEFINED": "some value",
    }

    settings = manager_core.Settings(required_keys, optional_keys)
    settings.location = create_test_config_file
    settings.cached_config = store_settings
    settings.update_config()

    return settings


@pytest.fixture
def default_init():
    return TrackedProgram.min_init("test", 100)


@pytest.fixture
def dict_params():
    attributes = {
        'name': 'test',
        'max_time': 100,
        'start_time': 0,
        'end_time': 0,
        'time_left': 100,
        'blocked': False
    }
    return attributes


@pytest.fixture(scope="function")
def program_class_fixture():
    test1 = TrackedProgram('test1', 100, 0, 0, 100)
    test2 = TrackedProgram('test2', 50, 0, 0, 50)
    test3 = TrackedProgram('test3', 25, 0, 0, 25)
    return test1, test2, test3


@pytest.fixture
def states_fixture_empty():
    with patch('manager_core.CurbTheScreen.ProgramStates.init_program_objs') as patched:
        patched.return_value = []
        ps = ProgramStates()
        return ps

import os
from pathlib import Path
from unittest.mock import patch

import pytest

import manager_core.SettingsParser as SettingsParser
import manager_core.Settings as Settings
from manager_core.CurbTheScreen import DataManager, TrackedProgram, ProgramStates

base_loc = Settings.Settings.get_base_loc(Settings.Settings.root_dir_name)
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

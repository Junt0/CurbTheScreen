import os
from pathlib import Path
import manager_core.CurbTheScreen as CTS
from manager_core.Settings import Settings
required_keys = [
    'LOOP_TIME',
    'TRACKED_PROGRAMS',
]

# The setting name and the default value
optional_keys = [
    ('TESTING', False),
    ('IS_BUILD', False),
    ('ROOT_DIR_NAME', Settings.root_dir_name),
]


if Settings.is_build:
    # Location of the config file in the build version
    Settings.location = Path("configuration") / 'config.json'
    CTS.DataManager.base_path = Settings.get_base_loc("CTS")
else:
    Settings.location = Settings.get_base_loc(Settings.root_dir_name) / 'manager_core' / "config.json"

settings = Settings(required_keys, optional_keys)
settings.reload_cache()

Settings.root_dir_name = settings.get_attr("ROOT_DIR_NAME")


@settings.add_parser
def TRACKED_PROGRAMS(setting_values: dict):
    parsed_pgs = []
    for key, value in setting_values.items():
        parsed_pgs.append(CTS.TrackedProgram.min_init(key, value))
    return parsed_pgs

import os
from pathlib import Path
import manager_core.CurbTheScreen as CTS
from manager_core.Settings import Settings

# The location where the config file is stored in the repo
Settings.location = Settings.get_base_loc(Settings.root_dir_name) / 'manager_core' / "config.json"

required_keys = [
    'ROOT_DIR_NAME',
    'LOOP_TIME',
    'TRACKED_PROGRAMS',
]

# The setting name and the default value
optional_keys = [
    ('TESTING', False),
    ('IS_BUILD', False),
]

settings = Settings(required_keys, optional_keys)


@settings.add_parser
def TRACKED_PROGRAMS(setting_values: dict):
    parsed_pgs = []
    for key, value in setting_values.items():
        parsed_pgs.append(CTS.TrackedProgram.min_init(key, value))
    return parsed_pgs

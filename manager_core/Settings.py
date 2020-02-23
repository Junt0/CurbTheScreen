import os

from pathlib2 import Path

ROOT_DIR_NAME = "CurbTheScreen"
def get_base_loc(dir_name):
    cur_dir_path = Path(os.getcwd())
    try:
        index = cur_dir_path.parts.index(dir_name)
    except ValueError:
        return None

    p = ""
    for part in range(0, index + 1):
        p += f'{cur_dir_path.parts[part]}/'

    return Path(p)


ROOT_LOC = get_base_loc(ROOT_DIR_NAME)

TESTING = False
TESTING_DB_LOC = os.path.join(ROOT_LOC, "database/test_db.sqlite")
SCHEMA_LOC = os.path.join(ROOT_LOC, 'database/schema.sql')
DB_LOC = os.path.join(ROOT_LOC, "database/db.sqlite")

LOOP_TIME = 1
TRACKED_PROGRAMS = [
    # Format ([program name], [max time seconds])
    ("Calculator", 10),
    ("Discord", 10),
]

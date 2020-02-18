import os

from CurbTheScreen import TrackedProgram

ROOT_DIR_NAME = "CurbTheScreen"
def get_base_loc(dir_name):
    cur_dir = os.getcwd().split("/")

    try:
        index = cur_dir.index(dir_name)
    except ValueError:
        return None

    return "/".join(cur_dir[0:index + 1])


ROOT_LOC = get_base_loc(ROOT_DIR_NAME)

TESTING = False
TESTING_DB_LOC = os.path.join(ROOT_LOC, "database/test_db.sqlite")
SCHEMA_LOC = os.path.join(ROOT_LOC, 'database/schema.sql')
DB_LOC = os.path.join(ROOT_LOC, "database/db.sqlite")

LOOP_TIME = 1
TRACKED_PROGRAMS = [
    # Format TrackedProgram.min_init([program name], [max running time seconds] )
    TrackedProgram.min_init("Calculator", 10)
]

import pytest
from manager_core.CurbTheScreen import DataManager, TrackedProgram


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

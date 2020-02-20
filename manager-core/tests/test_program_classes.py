from unittest.mock import patch

import pytest
import time
from CurbTheScreen import TrackedProgram


@pytest.fixture
def blank():
    return TrackedProgram("test", 1, 0, 0, 0)


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


@pytest.mark.parametrize("name, expected", [("test", True), (1, False), (1.0, False), (None, False)])
def test_name_valid(name, expected, blank):
    blank._name = name
    assert blank._is_name_valid(blank._name) == expected


@pytest.mark.parametrize("max_time, expected",
                         [("test", False), (1, True), (1.0, True), (None, False), (-1, False), (0, False)])
def test_max_time_valid(max_time, expected, blank):
    blank._max_time = max_time
    assert blank._is_max_time_valid(blank._max_time) == expected


@pytest.mark.parametrize("start_time, expected", [("test", False), (1, True), (1.0, True), (None, False), (-1, False)])
def test_start_time_valid(start_time, expected, blank):
    blank._start_time = start_time
    assert blank._is_float_or_int_not_neg(blank._start_time) == expected


@pytest.mark.parametrize("end_time, expected", [("test", False), (1, True), (1.0, True), (None, False), (-1, False)])
def test_end_time_valid(end_time, expected, blank):
    blank._end_time = end_time
    assert blank._is_float_or_int_not_neg(blank._end_time) == expected


@pytest.mark.parametrize("time_left, expected", [("test", False), (1, True), (1.0, True), (None, False), (-1, False)])
def test_time_left_valid(time_left, expected, blank):
    blank._time_left = time_left
    assert blank._is_float_or_int_not_neg(blank._time_left) == expected


# test full initialization of TrackedProgram
def test_init():
    pg = TrackedProgram("test", 2, 1, 2, 0)
    assert pg.name == "test"
    assert pg.max_time == 2
    assert pg.db_id is None
    assert pg.start_time == 1
    assert pg.end_time == 2
    assert pg.time_left == 0.0
    assert pg.blocked is False

# TODO add is valid edge case

# test minimum initialization of TrackedProgram
def test_min_init():
    pg = TrackedProgram.min_init("test", 10)
    assert pg.name == "test"
    assert pg.max_time == 10
    assert pg.db_id is None
    assert pg.start_time == 0
    assert pg.end_time == 0
    assert pg._time_left == 10.0
    assert pg.blocked is False


# test creation of TrackedProgram from dictionary
def test_from_dict(default_init, dict_params):
    pg = TrackedProgram.dict_init(dict_params)
    assert pg.name == default_init.name
    assert pg.max_time == default_init.max_time
    assert pg.db_id == default_init.db_id
    assert pg.start_time == default_init.start_time
    assert pg.end_time == default_init.end_time
    assert pg.time_left == default_init.time_left
    assert pg.blocked == default_init.blocked


# test start now
def test_start_now(default_init):
    start_time = int(time.time())
    with patch("manager-core.CurbTheScreen.time.time") as mocked_time:
        mocked_time.return_value = start_time
        default_init.start_now()
        assert default_init.start_time == start_time


# test end now
def test_end_now(default_init):
    end_time = int(time.time())
    with patch("manager-core.CurbTheScreen.time.time") as mocked_time:
        mocked_time.return_value = end_time
        default_init.end_now()
        assert default_init.end_time == end_time


# test update from other object
def test_update():
    # When first object has blanks
    blank = TrackedProgram("test", 1, 0, 0, 0)
    update_obj = TrackedProgram("test", 10, 20, 30, 40)
    blank.update(update_obj)

    assert blank.start_time == update_obj.start_time
    assert blank.end_time == update_obj.end_time
    assert blank.time_left == update_obj.time_left

    # When first object has all filled
    start = 20
    end = 30
    filled = TrackedProgram("test", 10, start, end, 40)
    update_obj = TrackedProgram("test", 50, 60, 70, 80)
    filled.update(update_obj)

    assert filled.start_time == start
    assert filled.end_time == end
    # time remaining is always updated regardless if its filled
    assert filled.time_left == update_obj.time_left


# default max time for test is 10 seconds
@pytest.mark.parametrize("start, end, time_left, expected", [
    (0, 0, 0, 10),
    (20, 0, 0, 0),
    (20, 0, 5, 5),
    (20, 30, 0, 0),
    (20, 30, 10, 10),
])
def test_time_left(start, end, time_left, expected):
    # 1. No start, no end, no time left
    # 2. Has start, no end, no time left
    # 3. Has start, no end, has time left
    # 4. Has start, has end, has no time left
    # 5. Has start, has end, has time left
    program = TrackedProgram("test", 10, start, end, time_left)
    program.elapsed_time = 0
    assert program.time_left == expected

# default max time for test is 10 seconds
#@pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.parametrize("start, end, time_left, elapsed, expected", [
    (0, 0, 0, 5, 10),
    (20, 0, 0, 5, 0),
    (20, 0, 10, 5, 5),
    (20, 30, 0, 5, 0),
    (20, 30, 10, 5, 5),
])
def test_time_left_w_elapsed(start, end, time_left, elapsed, expected):
    # 1. No start, no end, no time left, has elapsed (impossible)
    # 2. Has start, no end, no time left, has elapsed
    # 3. Has start, no end, has time left, has elapsed
    # 4. Has start, has end, has no time left, has elapsed
    # 5. Has start, has end, has time left, has elapsed
    program = TrackedProgram("test", 10, start, end, time_left)
    program.elapsed_time = elapsed
    assert program.time_left == expected

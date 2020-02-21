from unittest.mock import patch

import pytest
import time
from manager_core.CurbTheScreen import TrackedProgram, Program

# Tests to be added:
# TODO Check is_valid() is called on object initialization, raised exception if invalid
# TODO Add is_valid() start_none_no_end, start_none_no_elapsed tests


@pytest.fixture
def blank():
    return TrackedProgram("test", 1, 0, 0, 0)

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


class TestTrackedProgram:
    @pytest.mark.parametrize("name, expected", [("test", True), (1, False), (1.0, False), (None, False)])
    def test_name_valid(self, name, expected, blank):
        blank._name = name
        assert blank._is_name_valid(blank._name) == expected

    @pytest.mark.parametrize("max_time, expected",
                             [("test", False), (1, True), (1.0, True), (None, False), (-1, False), (0, False)])
    def test_max_time_valid(self, max_time, expected, blank):
        blank._max_time = max_time
        assert blank._is_max_time_valid(blank._max_time) == expected

    @pytest.mark.parametrize("start_time, expected",
                             [("test", False), (1, True), (1.0, True), (None, False), (-1, False)])
    def test_start_time_valid(self, start_time, expected, blank):
        blank._start_time = start_time
        assert blank._is_float_or_int_not_neg(blank._start_time) == expected

    @pytest.mark.parametrize("end_time, expected",
                             [("test", False), (1, True), (1.0, True), (None, False), (-1, False)])
    def test_end_time_valid(self, end_time, expected, blank):
        blank._end_time = end_time
        assert blank._is_float_or_int_not_neg(blank._end_time) == expected

    @pytest.mark.parametrize("time_left, expected",
                             [("test", False), (1, True), (1.0, True), (None, False), (-1, False)])
    def test_time_left_valid(self, time_left, expected, blank):
        blank._time_left = time_left
        assert blank._is_float_or_int_not_neg(blank._time_left) == expected

    # test full initialization of TrackedProgram
    def test_init(self, ):
        pg = TrackedProgram("test", 2, 1, 2, 0)
        assert pg.name == "test"
        assert pg.max_time == 2
        assert pg.db_id is None
        assert pg.start_time == 1
        assert pg.end_time == 2
        assert pg.time_left == 0.0
        assert pg.blocked is False

    # test minimum initialization of TrackedProgram
    def test_min_init(self, ):
        pg = TrackedProgram.min_init("test", 10)
        assert pg.name == "test"
        assert pg.max_time == 10
        assert pg.db_id is None
        assert pg.start_time == 0
        assert pg.end_time == 0
        assert pg._time_left == 10.0
        assert pg.blocked is False

    # test creation of TrackedProgram from dictionary
    def test_from_dict(self, default_init, dict_params):
        pg = TrackedProgram.dict_init(dict_params)
        assert pg.name == default_init.name
        assert pg.max_time == default_init.max_time
        assert pg.db_id == default_init.db_id
        assert pg.start_time == default_init.start_time
        assert pg.end_time == default_init.end_time
        assert pg.time_left == default_init.time_left
        assert pg.blocked == default_init.blocked

    # test start now
    def test_start_now(self, default_init):
        start_time = int(time.time())
        with patch("manager_core.CurbTheScreen.time.time") as mocked_time:
            mocked_time.return_value = start_time
            default_init.start_now()
            assert default_init.start_time == start_time

    # test end now
    def test_end_now(self, default_init):
        end_time = int(time.time())
        with patch("manager_core.CurbTheScreen.time.time") as mocked_time:
            mocked_time.return_value = end_time
            default_init.end_now()
            assert default_init.end_time == end_time

    # default max time for test is 10 seconds
    @pytest.mark.parametrize("start, end, time_left, expected", [
        (0, 0, 0, 10),
        (20, 0, 0, 0),
        (20, 0, 5, 5),
        (20, 30, 0, 0),
        (20, 30, 10, 10),
    ])
    def test_time_left(self, start, end, time_left, expected):
        # 1. No start, no end, no time left
        # 2. Has start, no end, no time left
        # 3. Has start, no end, has time left
        # 4. Has start, has end, has no time left
        # 5. Has start, has end, has time left
        program = TrackedProgram("test", 10, start, end, time_left)
        program.elapsed_time = 0
        assert program.time_left == expected

    # default max time for test is 10 seconds
    @pytest.mark.parametrize("start, end, time_left, elapsed, expected", [
        (0, 0, 0, 5, 10),
        (20, 0, 0, 5, 0),
        (20, 0, 10, 5, 5),
        (20, 30, 0, 5, 0),
        (20, 30, 10, 5, 5),
    ])
    def test_time_left_w_elapsed(self, start, end, time_left, elapsed, expected):
        # 1. No start, no end, no time left, has elapsed (impossible)
        # 2. Has start, no end, no time left, has elapsed
        # 3. Has start, no end, has time left, has elapsed
        # 4. Has start, has end, has no time left, has elapsed
        # 5. Has start, has end, has time left, has elapsed
        program = TrackedProgram("test", 10, start, end, time_left)
        program.elapsed_time = elapsed
        assert program.time_left == expected

    @pytest.mark.parametrize("name, blocked, start, end, max_time, time_left, expected", [
        ("test", False, 0, 0, 100, 100, True),
        ("test", False, 0, 0, 100, 0, True),
        ("test", True, 0, 0, 100, 100, False),
        ("not right", False, 0, 0, 100, 100, False),
        ("test", False, 1, 0, 100, 100, False),
    ])
    def test_equal(self, default_init, name, blocked, start, end, max_time, time_left, expected):
        pg1 = TrackedProgram(name, max_time, start, end, time_left)
        pg1.blocked = blocked
        result = pg1 == default_init
        assert result == expected


@pytest.fixture()
def example_pg_class():
    pg = Program(TrackedProgram.min_init("test", 100))
    return pg


class TestTrackProgramSubclass:

    def test_program_add_pid(self, example_pg_class):
        pg = example_pg_class
        pg.add_pid(1)
        pg.add_pid(2)
        pg.add_pid(3)
        pg.add_pid(3)
        assert pg.PIDS == [1, 2, 3]

    def test_reset_pids(self, example_pg_class):
        pg = example_pg_class
        pg.PIDS = [1, 2]
        pg.reset_pids()
        assert pg.PIDS == []

    def test_is_running(self, example_pg_class):
        pg = example_pg_class
        assert pg.is_running() is False

        pg.PIDS = [1, 2]
        assert pg.is_running() is True

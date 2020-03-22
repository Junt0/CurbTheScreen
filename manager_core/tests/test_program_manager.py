from unittest.mock import patch

import pytest
from manager_core.CurbTheScreen import Program, ProgramManager


@pytest.fixture(scope="function")
def pg_manager_blank_fixture(states_fixture_empty):
    return ProgramManager(states_fixture_empty)


# TODO figure out how to test that .kill() is called on process object
def test_kill(default_init):
    pg_manager = ProgramManager(None)

    # Tests that pids are reset and process is made with the pid (
    pg = Program(default_init)
    pid1 = 1
    pg.PIDS = [pid1]

    with patch("manager_core.CurbTheScreen.psutil.Process") as mocked_process:
        with patch("manager_core.CurbTheScreen.psutil.Process.kill") as mocked_kill:
            mocked_kill.return_value = None
            pg_manager.kill(pg)
            mocked_process.assert_called_with(pid1)


@pytest.mark.parametrize("time_left, blocked, in_arr, expected", [
    (0, False, False, True),
    (100, True, False, True),
    (100, False, True, True),
    (100, False, False, False)
])
def test_is_blocked(pg_manager_blank_fixture, default_init, time_left, blocked, in_arr, expected):
    # 1. When time left is 0
    # 2. When marked as blocked
    # 3. When marked as blocked
    # 4. When it has time left, is not blocked and not in arr
    manager = pg_manager_blank_fixture

    if in_arr:
        manager.blocked_programs.append(default_init)

    default_init.time_left = time_left
    default_init.blocked = blocked
    assert manager.is_blocked(default_init) is expected


def test_add_to_blocked(default_init, pg_manager_blank_fixture):
    manager = pg_manager_blank_fixture

    # The program is blocked and is added to the arr
    with patch("manager_core.CurbTheScreen.ProgramManager.is_blocked") as patched_blocked:
        patched_blocked.return_value = True
        manager.blocked_programs = []
        manager.add_to_blocked(default_init)

        assert manager.blocked_programs[0] == default_init

        # Checks that blocked and time_left values are updated to be consistent in case they dont match
        assert manager.blocked_programs[0].time_left == 0
        assert manager.blocked_programs[0].blocked is True

        # The program is blocked but is already in the arr
        patched_blocked.return_value = True
        manager.blocked_programs = [default_init]
        manager.add_to_blocked(default_init)
        assert len(manager.blocked_programs) == 1


def test_update_blocked(program_class_fixture, pg_manager_blank_fixture):
    # Tests that they are added to the block when they are blocked
    program_arr = []
    for program in program_class_fixture:
        pg = Program(program)
        pg.blocked = True
        program_arr.append(pg)

    manager = pg_manager_blank_fixture
    program_states = manager.PS
    program_states.program_objs = program_arr

    manager.update_blocked()

    assert manager.blocked_programs == program_arr


def test_prune_programs(program_class_fixture, pg_manager_blank_fixture):
    manager = pg_manager_blank_fixture

    # Given an array with some blocked and some not, returns only the not blocked and adds the blocked to the manager
    programs = program_class_fixture
    programs[1].blocked = True

    with patch("manager_core.CurbTheScreen.ProgramManager.kill") as patched_kill:
        result = manager.prune_programs(program_class_fixture)
        assert result == [programs[0], programs[2]]
        assert manager.blocked_programs == [programs[1]]

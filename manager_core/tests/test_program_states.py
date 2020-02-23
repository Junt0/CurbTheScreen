from unittest.mock import patch

import pytest

from manager_core.CurbTheScreen import TrackedProgram, Program, ProgramStates


@pytest.fixture
def states_fixture_full(states_fixture_empty, program_class_fixture):
    ps = states_fixture_empty

    program_arr = []
    for program in program_class_fixture:
        pg = Program(program)
        program_arr.append(pg)

    ps.program_objs = program_arr

    return ps


def test_init_program_objs_no_save(program_class_fixture):
    # Tests that the program objs are loaded in from the settings file directly if there is no save
    with patch('manager_core.CurbTheScreen.ProgramStates.tracked_from_settings') as patched_settings:
        patched_settings.return_value = program_class_fixture
        with patch('manager_core.CurbTheScreen.DataManager.get_latest_save') as patched_save:
            patched_save.return_value = None
            ps = ProgramStates()

            assert ps.program_objs[0] == program_class_fixture[0]
            assert ps.program_objs[1] == program_class_fixture[1]
            assert ps.program_objs[2] == program_class_fixture[2]


@pytest.mark.parametrize("time_left, expected_left, expected_block", [
    (90, 90, False),
    (0, 0, True)
])
def test_init_program_objs_with_save_no_db(time_left, expected_left, expected_block):
    # Tests if there is a saved program and it updates only the time left and blocked status
    test1 = TrackedProgram.min_init("test1", 100)
    test1_saved = TrackedProgram("test1", 100, 50, 60, time_left)

    with patch('manager_core.CurbTheScreen.ProgramStates.tracked_from_settings') as tracked:
        tracked.return_value = [test1]
        with patch('manager_core.CurbTheScreen.TrackedProgram.has_save_today') as has_save:
            has_save.return_value = True
            with patch('manager_core.CurbTheScreen.DataManager.get_latest_save') as latest_save:
                latest_save.return_value = test1_saved
                ps = ProgramStates()

                assert ps.program_objs[0].time_left == expected_left
                assert ps.program_objs[0].blocked == expected_block


def test_update_elapsed(program_class_fixture, states_fixture_empty):
    # Tests that for all programs that are in currently running the elapsed time is increased when method is called
    test1, test2, test3 = program_class_fixture

    ps = states_fixture_empty
    ps.currently_running = program_class_fixture

    with patch('manager_core.CurbTheScreen.ProgramStates.get_loop_time') as loop_time:
        loop_time.return_value = 1

        ps.update_elapsed()

        assert test1.elapsed_time == 1
        assert test2.elapsed_time == 1
        assert test3.elapsed_time == 1


def test_reset(program_class_fixture):
    # Tests that the PIDS for all program objects are reset
    with patch('manager_core.CurbTheScreen.ProgramStates.tracked_from_settings') as patched:
        patched.return_value = program_class_fixture

        with patch('manager_core.CurbTheScreen.TrackedProgram.has_save_today') as has_save:
            has_save.return_value = False
            ps = ProgramStates()

            for program in ps.program_objs:
                program.add_pid(1)
                assert program.PIDS == [1]

            ps.reset()
            for program in ps.program_objs:
                assert program.PIDS == []


def test_populate_program_pids(states_fixture_full):
    ps = states_fixture_full

    with patch('manager_core.CurbTheScreen.psutil.process_iter') as mocked_process_iter:
        with patch('manager_core.CurbTheScreen.psutil.Process') as mocked_process:
            temp_program = TrackedProgram.min_init("test1", 100)

            # Tests when pids are added that match the name of the program
            mocked_process.info = {"name": 'test1', "pid": 1}
            mocked_process_iter.return_value = iter([mocked_process])
            ps.populate_program_pids()
            mocked_process_iter.assert_called_with(attrs=["name", "pid"])

            assert [1] == ps.get_program(temp_program).PIDS

            mocked_process.info = {"name": 'test1', "pid": 2}
            mocked_process_iter.return_value = iter([mocked_process])
            ps.populate_program_pids()

            assert [1, 2] == ps.get_program(temp_program).PIDS

            # Tests that the program is retrieved when it contains the name of the program
            mocked_process.info = {"name": 'Containstest1', "pid": 3}
            mocked_process_iter.return_value = iter([mocked_process])

            ps.populate_program_pids()
            assert [1, 2, 3] == ps.get_program(temp_program).PIDS

            # Tests when the name is not contained
            # Tests that the program is retrieved when it contains the name of the program
            mocked_process.info = {"name": 'test42', "pid": 10}
            mocked_process_iter.return_value = iter([mocked_process])

            ps.populate_program_pids()
            assert [1, 2, 3] == ps.get_program(temp_program).PIDS


def test_add_to_running(states_fixture_full):
    ps = states_fixture_full

    test1 = ps.program_objs[0]
    test2 = ps.program_objs[1]

    test1.PIDS = [1, 2]
    test2.PIDS = [3, 4]

    assert ps.currently_running == []

    ps.add_to_running()

    assert ps.currently_running == [test1, test2]


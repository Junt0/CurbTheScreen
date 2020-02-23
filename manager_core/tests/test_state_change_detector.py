from unittest.mock import patch

import pytest
import time
from manager_core.CurbTheScreen import TrackedProgram, Program, ProgramStates, DataManager, StateChangeDetector


@pytest.fixture(scope="function")
def state_change_blank_fixture():
    return StateChangeDetector()


"""@pytest.fixture(scope="function")
def state_change_filled_fixture(default_init):
    pg1 = default_init
    pg1_diff = TrackedProgram.min_init("test2", 200)
    pg3 = TrackedProgram.min_init("test3", 300)
    pg4 = TrackedProgram.min_init("test4", 400)
    prev_programs
"""


def test_state_change_detector_init(state_change_blank_fixture):
    # Tests that the prev_state and curr_state arrays are initialized as blank
    state_detector = state_change_blank_fixture
    assert state_detector.prev_state == []
    assert state_detector.curr_state == []


def test_state_change_update_states(state_change_blank_fixture, default_init):
    # Test that the arrays are updated after being given the current state
    state_detector = state_change_blank_fixture
    programs1 = [default_init, default_init]
    state_detector.update_states(programs1)

    # One pass of updating
    assert state_detector.curr_state == programs1
    assert state_detector.prev_state == []

    # Second pass of updating
    programs2 = [default_init]
    state_detector.update_states(programs2)
    assert state_detector.curr_state == programs2
    assert state_detector.prev_state == programs1


def test_get_program_from_arr(state_change_blank_fixture, default_init):
    state_detector = state_change_blank_fixture
    program1 = default_init
    program2 = TrackedProgram.min_init("test2", 200)
    all_programs = [program1, program2]
    state_detector.curr_state = all_programs

    # Retrieves the same program, but may not be the same instance. Is based off of name
    retrieved_pg = state_detector.get_program(TrackedProgram.min_init("test2", 500), state_detector.curr_state)
    assert retrieved_pg == program2


@pytest.mark.parametrize("curr_state, prev_state, expected", [
    ("pg", "pg", False), ("", "pg", True), ("pg", "", False), ("", "", False)
])
def test_is_stopped(state_change_blank_fixture, default_init, curr_state, prev_state, expected):
    # Returns whether or not the program is running based on the arrays its in
    # 1. Program in curr_state and prev_state
    # 2. Program not in curr_state and in prev_state
    # 3. Program in curr_state and not in prev_state
    # 4. Program not in curr_state and not in prev_state

    state_detector = state_change_blank_fixture
    program1 = default_init

    if curr_state == "pg":
        state_detector.curr_state = [program1]
    else:
        state_detector.curr_state = []

    if prev_state == "pg":
        state_detector.prev_state = [program1]
    else:
        state_detector.prev_state = []

    assert state_detector.is_stopped(program1) is expected


@pytest.mark.parametrize("curr_state, prev_state, expected", [
    ("pg", "pg", False), ("", "pg", False), ("pg", "", True), ("", "", False)
])
def test_is_started(state_change_blank_fixture, default_init, curr_state, prev_state, expected):
    # Returns whether or not the program is running based on the arrays its in
    # 1. Program in curr_state and prev_state
    # 2. Program not in curr_state and in prev_state
    # 3. Program in curr_state and not in prev_state
    # 4. Program not in curr_state and not in prev_state

    state_detector = state_change_blank_fixture
    program1 = default_init

    if curr_state == "pg":
        state_detector.curr_state = [program1]
    else:
        state_detector.curr_state = []

    if prev_state == "pg":
        state_detector.prev_state = [program1]
    else:
        state_detector.prev_state = []

    assert state_detector.is_started(program1) is expected


def test_get_started_mocked_saves(state_change_blank_fixture, default_init):
    # When there are items populated
    state_detector = state_change_blank_fixture
    state_detector.curr_state = [default_init]

    with patch("manager_core.CurbTheScreen.LoadData.prev_logged_save") as patch_load:
        state_detector.get_started()
        patch_load.assert_called_with([default_init])

    # When there are no items populated
    state_detector = state_change_blank_fixture
    state_detector.curr_state = []

    with patch("manager_core.CurbTheScreen.LoadData.prev_logged_save") as patch_load:
        state_detector.get_started()
        patch_load.assert_called_with([])


def test_get_ended(state_change_blank_fixture, default_init):
    state_detector = state_change_blank_fixture

    # When there are items populated
    state_detector.prev_state = [default_init]
    assert state_detector.get_stopped() == [default_init]

    # When there are no items populated
    state_detector.prev_state = []
    assert state_detector.get_stopped() == []

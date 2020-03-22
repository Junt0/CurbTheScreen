import pytest
from manager_core.CurbTheScreen import TrackedProgram
from manager_core.SettingsParser import settings


def test_TRACKED_PROGRAMS_parser(settings_fixture):
    tracked_programs = {
        "a": 10,
        "b": 10,
        "c": 20
    }
    settings.update_setting("TRACKED_PROGRAMS", tracked_programs)

    a = TrackedProgram.min_init("a", tracked_programs["a"])
    b = TrackedProgram.min_init("b", tracked_programs["b"])
    c = TrackedProgram.min_init("c", tracked_programs["c"])
    programs = [a, b, c]

    assert programs == settings.get_attr("TRACKED_PROGRAMS")

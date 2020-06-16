import pytest
from manager_core.CurbTheScreen import TrackedProgram
from manager_core.SettingsParser import settings
from manager_core.groups import Settings, SettingsChunk, SettingsRetrieval, Parser, ChunkTemplate

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

def test_new_parser():
    test_json = {
        "ROOT_DIR_NAME": "CurbTheScreen",
        "LOOP_TIME": 1,
        "GROUPS": {
            "group1": {
                "TYPE": "default",
                "TRACKED_PROGRAMS": {
                    "Calculator": 1000,
                    "Discord": 1000,
                    "Chrome": 1000
                }
            },

            "group2": {
                "TYPE": "totaltime",
                "total_time": 1000,
                "TRACKED_PROGRAMS": ["Calculator", "Discord", "Chrome"]
            }
        }
    }
    my_settings = Settings(
        parsers=[Parser("ROOT_DIR_NAME"), Parser("LOOP_TIME")],
        
        chunks=[
            SettingsChunk(
                name="GROUPS",
                chunks=[
                    ChunkTemplate(
                        chunk_type="default",
                        required=['TRACKED_PROGRAMS'],
                        parsers=[Parser("TYPE")],
                    ),
                    ChunkTemplate(
                        chunk_type="totaltime",
                        required=['TRACKED_PROGRAMS', 'TOTAL_TIME'],
                        parsers=[Parser("TYPE"), Parser("TotalTime")],
                    )
                ]
            )    
        ]
    )

    my_settings.is_valid()
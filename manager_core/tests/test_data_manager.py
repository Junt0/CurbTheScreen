import sqlite3
from datetime import datetime, timedelta
from manager_core.CurbTheScreen import DataManager, TrackedProgram

import pytest


@pytest.fixture(scope="function")
def store_example(create_db):
    with DataManager.StoreData(DataManager) as db:
        name = "test"
        start, end_time, time_left = (0, 0, 0)
        max_time = 10
        command = f"INSERT INTO program_log (name, start_time, end_time, time_left, max_time) VALUES('{name}', {start}, {end_time}, {time_left}, {max_time})"
        db.execute(command)

        return name, start, end_time, time_left, max_time


@pytest.fixture(scope="function")
def date_fixture(create_db):
    base = datetime(2020, 11, 1)
    date1 = base + timedelta(days=1)
    date2 = base + timedelta(days=2)
    date3 = base + timedelta(days=3)
    offset = 1000

    test1 = TrackedProgram("test1", 10, base.timestamp(), base.timestamp() + offset, 100)
    test2 = TrackedProgram("test2", 10, date1.timestamp(), date1.timestamp() + offset, 100)
    test3 = TrackedProgram("test2", 10, date2.timestamp(), date2.timestamp() + offset, 100)
    test4 = TrackedProgram("test4", 10, date3.timestamp(), date3.timestamp() + offset, 100)
    DataManager.store_many(test1, test2, test3, test4)

    date_values = {
        "test_objs": (test1, test2, test3, test4),
        "date_objs": (base, date1, date2, date3)
    }

    return date_values


def test_db_query(reset_db, store_example):
    # Tests that a single row object is retrieved
    name, start, end_time, time_left, max_time = store_example
    result = DataManager.query("SELECT * FROM program_log", single=True)

    assert len(result) == 6
    assert result["name"] == name
    assert result["start_time"] == start
    assert result["end_time"] == end_time
    assert result["time_left"] == time_left
    assert result["max_time"] == max_time

    # Tests that an array of row objects is returned
    result = DataManager.query("SELECT * FROM program_log;")

    assert len(result) == 1


def test_to_obj_valid(reset_db, store_example):
    # Tests that a TrackedProgram object is initialized correctly with valid values
    name, start, end_time, time_left, max_time = store_example
    result = DataManager.query("SELECT * FROM program_log", single=True)
    obj = DataManager.to_obj(result)

    assert obj.db_id == 1
    assert obj.name == name
    assert obj.start_time == start
    assert obj.end_time == end_time
    assert obj._time_left == time_left
    assert obj.max_time == max_time


@pytest.mark.parametrize("attribute, value",
                         [("name", 0), ("start_time", ""), ("end_time", ""), ("time_left", ""), ("max_time", "")])
def test_to_obj_invalid(reset_db, dict_params, attribute, value):
    # Tests that exception is raised from invalid value
    dict_params[attribute] = value
    dict_params[attribute] = value
    with pytest.raises(ValueError) as e_info:
        obj = DataManager.to_obj(dict_params)


def test_store_new_valid(reset_db, default_init):
    # Test when TrackedProgram is valid
    DataManager.store_new(default_init)
    result = DataManager.query("SELECT * FROM program_log", single=True)

    assert result['start_time'] == default_init.start_time
    assert result['end_time'] == default_init.end_time
    assert result['time_left'] == default_init.time_left
    assert result['max_time'] == default_init.max_time
    assert result['name'] == default_init.name
    assert result['id'] is 1


@pytest.mark.parametrize("row_num", [row_num for row_num in range(2)])
def test_store_many(reset_db, default_init, row_num):
    DataManager.store_many(default_init, default_init)

    result = DataManager.query("SELECT * FROM program_log")
    result = result[row_num]

    assert result['start_time'] == default_init.start_time
    assert result['end_time'] == default_init.end_time
    assert result['time_left'] == default_init.time_left
    assert result['max_time'] == default_init.max_time
    assert result['name'] == default_init.name
    assert result['id'] is row_num + 1


@pytest.mark.parametrize("params, expected", [
    ({"p1": 10}, "p1=10"),
    ({"p1": "test"}, "p1='test'"),
    ({"p1": 10, "p2": 20}, "p1=10 AND p2=20"),
    ({"p1": "test1", "p2": "test2"}, "p1='test1' AND p2='test2'"),
    ({"p1": "test1", "p2": 20}, "p1='test1' AND p2=20"),

])
def test_chain_filter_helper(params, expected):
    # 1. Single int param
    # 2. Single str param
    # 3. Multiple param, 2 int
    # 4. Multiple param, 2 str
    # 4. Multiple param, 1 str 1 int
    assert DataManager._chain_filter_helper(params, " AND ") == expected


def test_get(reset_db, default_init):
    DataManager.store_new(default_init)
    result = DataManager.get(name=default_init.name)
    assert result == default_init


def test_get_many(reset_db, default_init):
    DataManager.store_many(default_init, default_init)
    result = DataManager.get_many(name=default_init.name)
    assert result[0] == default_init
    assert result[1] == default_init


def test_id_of_obj(reset_db, default_init):
    DataManager.store_new(default_init)
    assert DataManager.id_of_obj(default_init) == 1


def test_update_pg(reset_db, default_init):
    start_time = 10
    end_time = 20

    DataManager.store_new(default_init)
    id = DataManager.id_of_obj(default_init)
    DataManager.update_pg(id, start_time=start_time, end_time=end_time)
    from_db = DataManager.get(name=default_init.name)

    assert from_db.start_time != default_init.start_time
    assert from_db.end_time != default_init.end_time
    assert from_db.start_time == start_time
    assert from_db.end_time == end_time


# TODO test datetime
def test_date_range(reset_db, date_fixture):
    base, date1, date2, date3 = date_fixture['date_objs']
    test1, test2, test3, test4 = date_fixture['test_objs']
    offset = 1000

    # 1. Same start time, Same end time
    results = DataManager.get_date_range(base, base + timedelta(seconds=offset))
    assert results == [test1]

    # 2. Start time > query start, end time < query end
    results = DataManager.get_date_range(date1, date2)
    assert results == [test2, test3]

    # 3. Start time < query_start and start time < query end
    results = DataManager.get_date_range(date1, date2)
    assert results == [test2, test3]

    # 4. Start time > query end but has args
    results = DataManager.get_date_range(date2, date3, name="test1")
    assert results == []

    results = DataManager.get_date_range(base, date3, name="test1")
    assert results == [test1]


def test_get_day(reset_db, date_fixture):
    base, date1, date2, date3 = date_fixture['date_objs']
    test1, test2, test3, test4 = date_fixture['test_objs']
    offset = 1000

    # Test getting a single days result
    day_results = DataManager.get_day(base)
    assert [test1] == day_results

    day_results = DataManager.get_day(date1)
    assert [test2] == day_results

    # Tests with a filtering argument
    day_results = DataManager.get_day(base, name="test5")
    assert [] == day_results

    # Getting multiple objects that are in the same day
    test5 = TrackedProgram("test5", 10, base.timestamp() + offset, base.timestamp() + 2 * offset, 10)
    DataManager.store_new(test5)

    day_results = DataManager.get_day(base)
    assert [test1, test5] == day_results

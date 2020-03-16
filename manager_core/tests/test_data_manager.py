from datetime import datetime, timedelta

import pytest

from manager_core.CurbTheScreen import DataManager, TrackedProgram


# Tests to be added
# TODO test to_objs many

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


def test_store_many_none(reset_db, default_init):
    # Testing for bug where if no object is given to store_many it shows that an error occured with the db
    DataManager.store_many()

    result = DataManager.query("SELECT * FROM program_log")
    assert result == []


@pytest.mark.parametrize("query_params, expected", [
    ({"p1": 10}, "p1=10"),
    ({"p1": "test"}, "p1='test'"),
    ({"p1": 10, "p2": 20}, "p1=10 AND p2=20"),
    ({"p1": "test1", "p2": "test2"}, "p1='test1' AND p2='test2'"),
    ({"p1": "test1", "p2": 20}, "p1='test1' AND p2=20"),

])
def test_chain_filter_helper(query_params, expected):
    # 1. Single int param
    # 2. Single str param
    # 3. Multiple param, 2 int
    # 4. Multiple param, 2 str
    # 4. Multiple param, 1 str 1 int
    assert DataManager._chain_filter_helper(query_params, " AND ") == expected


def test_chain_filter_helper_nested_query():
    separator = " AND "
    params = {
        "p1": 10,
        "p2": 10,
        "p3": "Q| (SELECT MAX(some_value) FROM some_table)"
    }
    expected = "p1=10 AND p2=10 AND p3=(SELECT MAX(some_value) FROM some_table)"


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


def test_get_latest_save(reset_db):
    base_date = datetime.today().timestamp()
    # Programs that ran on a past date
    program1_a = TrackedProgram("test1", 100, 200, 300, 0)
    program2_a = TrackedProgram("test2", 100, 300, 375, 25)

    # Tests that the most current program from the current day is retrieved
    time_offset = 100
    program1_b = TrackedProgram("test1", 100, base_date, base_date + 50, 50)
    program1_c = TrackedProgram("test1", 100, base_date + time_offset, base_date + time_offset + 75, 25)
    program2_b = TrackedProgram("test2", 100, base_date + 2 * time_offset, base_date + 2 * time_offset + 100, 0)

    programs = [program1_a, program2_a, program1_b, program2_b, program1_c]
    DataManager.store_many(*programs)

    program1_blank = TrackedProgram.min_init("test1", 100)
    program2_blank = TrackedProgram.min_init("test2", 100)

    latest_1 = DataManager.get_latest_save(program1_blank)
    latest_2 = DataManager.get_latest_save(program2_blank)

    assert latest_1 == program1_c
    assert latest_2 == program2_b


def test_get_latest_save_empty(reset_db):
    base_date = datetime.today().timestamp()
    # Programs that ran on a past date
    program1_a = TrackedProgram("test1", 100, 200, 300, 0)
    program2_a = TrackedProgram("test2", 100, 300, 375, 25)

    programs = [program1_a, program2_a]
    DataManager.store_many(*programs)

    program1_blank = TrackedProgram.min_init("test1", 100)
    program2_blank = TrackedProgram.min_init("test2", 100)

    latest_1 = DataManager.get_latest_save(program1_blank)
    latest_2 = DataManager.get_latest_save(program2_blank)

    assert latest_1 == None
    assert latest_2 == None


def test_update_pg_times_end_filled(reset_db):
    base = datetime.today()
    offset = 10

    test2_a = TrackedProgram("test2", 100, base.timestamp(), base.timestamp() + offset, 90)

    new_end = base.timestamp() + 2 * offset
    test2_b = TrackedProgram("test2", 100, base.timestamp(), new_end, 80)

    DataManager.store_many(test2_a)
    DataManager.update_pg_times([test2_b])

    db_result = DataManager.get_latest_save(test2_a)
    assert db_result.time_left == 80
    assert db_result.end_time == new_end

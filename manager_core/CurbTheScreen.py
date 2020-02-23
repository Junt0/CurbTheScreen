import os
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib2 import Path
from typing import Union, List

import psutil

# Is a stripped down program object to differentiate between running programs and given programs to track
from . import Settings


# TODO add type hints for all classes
class TrackedProgram:
    def __init__(self, name, max_time, start, end, remaining):
        self.elapsed_time = 0
        self.blocked = False
        self.db_id = None

        self._name = name
        self._max_time = max_time
        self._start_time = start
        self._end_time = end

        self.time_left = remaining

        if self.is_valid() is False:
            raise AttributeError("Initialized with an invalid attribute")

    @classmethod
    def dict_init(cls, attrs):
        if attrs is None:
            return None

        program = TrackedProgram("", 1, 0, 0, 0)
        for key in attrs.keys():
            if key == "id":
                setattr(program, "db_id", attrs[key])
                continue
            setattr(program, key, attrs[key])
        return program

    @classmethod
    def min_init(cls, name, max_time):
        return TrackedProgram(name, max_time, 0, 0, max_time)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):

        if self._is_name_valid(value):
            self._name = value
        else:
            raise ValueError("Invalid value assigned to name")

    @property
    def max_time(self):
        return self._max_time

    @max_time.setter
    def max_time(self, value):
        if self._is_max_time_valid(value):
            self._max_time = float(value)
        else:
            raise ValueError("Invalid value assigned to max_time")

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        if self._is_float_or_int_not_neg(value):
            self._start_time = float(value)
        else:
            raise ValueError("Invalid value assigned to start_time")

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        if self._is_float_or_int_not_neg(value):
            self._end_time = float(value)
        else:
            raise ValueError("Invalid value assigned to end_time")

    @property
    def time_left(self):
        left = 0

        if self.start_time == 0 and self.end_time == 0:
            if self.max_time != self._time_left:
                left = self._time_left
            else:
                left = self.max_time
        elif self.start_time != 0 and (self.end_time == 0 or self.end_time != 0):
            if self._time_left == 0:
                left = 0
            else:
                left = self._time_left - self.elapsed_time

        return left

    @time_left.setter
    def time_left(self, value):
        if self._is_float_or_int_not_neg(value):
            self._time_left = value
        else:
            raise ValueError("Invalid value assigned to time_left")

    def start_now(self):
        self.start_time = int(time.time())

    def end_now(self):
        self.end_time = int(time.time())

    def is_valid(self):
        num_vars = [self.start_time, self.end_time, self.time_left]

        # if it has no start, it can't have an end
        start_none_no_end = not (self.start_time == 0 and self.end_time != 0)

        # can't have an elapsed time if there is no start
        start_none_no_elapsed = not (self.start_time == 0 and self.elapsed_time != 0)

        return self._is_name_valid(self.name) and self._is_max_time_valid(
            self.max_time) and self._is_float_or_int_not_neg_arr(
            num_vars) and start_none_no_end and start_none_no_elapsed

    def _is_max_time_valid(self, value):
        not_0 = value != 0
        is_float_or_int = self._is_float_or_int_not_neg(value)

        return not_0 and is_float_or_int

    def _is_name_valid(self, value):
        is_str = type(value) is str
        not_empty = is_str is not ""
        return is_str and not_empty

    def _is_float_or_int_not_neg(self, value):
        right_type = self._is_float(value) or self._is_int(value)

        right_sign = False
        if right_type:
            right_sign = not self._is_negative(value)

        return right_type and right_sign and not self._is_none(value)

    def _is_float_or_int_not_neg_arr(self, items):
        for variable in items:
            if self._is_float_or_int_not_neg(variable) is False:
                return False
        return True

    def _is_float(self, value):
        return type(value) is float

    def _is_int(self, value):
        return type(value) is int

    def _is_negative(self, value):
        return value < 0

    def _is_none(self, value):
        return value is None

    def has_save(self):
        game_inst = DataManager.get_day(datetime.today(), limit=None, name=self.name)
        if len(game_inst) is 0 or game_inst is None:
            return False
        return True

    def get_latest_save(self):
        # TODO make custom database query instead of querying multiple and finding lowest value
        if self.has_save() is True:
            program_saves = DataManager.get_day(datetime.today(), limit=None, name=self.name)

            time_min = (0, None)
            for pg in program_saves:
                if pg.end_time == 0:
                    return pg

                if pg.start_time > time_min[0]:
                    time_min = (pg.start_time, pg)

            return time_min[1]
        else:
            return None

    def __str__(self):
        return f"{self.name} S:{self.start_time}  E:{self.end_time}  R:{self.time_left()}"

    def __eq__(self, other):
        name_equal = other.name == self.name
        start_time_equal = other.start_time == self.start_time
        end_time_equal = other.end_time == self.end_time
        max_time_equal = other.max_time == self.max_time
        blocked_equal = other.blocked == self.blocked
        time_left_equal = other.time_left == self.time_left

        return blocked_equal and name_equal and start_time_equal and end_time_equal and max_time_equal and time_left_equal


# How the programs that are tracked will be represented
class Program(TrackedProgram):

    def __init__(self, tracked: TrackedProgram):
        super().__init__(tracked.name, tracked.max_time, tracked.start_time, tracked.end_time, tracked.time_left)
        self.PIDS = []

    def add_pid(self, pid):
        if pid not in self.PIDS:
            self.PIDS.append(pid)

    def reset_pids(self):
        self.PIDS = []

    def is_running(self):
        return len(self.PIDS) > 0

    @classmethod
    def get_program(cls, program, array):
        for item in array:
            if program.name == item.name:
                return item
        return None


# Stores any changes made into the database
class DataManager:
    path = None

    @classmethod
    def init_db(cls, path: Path):
        DataManager.path = path / "test_db.sqlite"
        """if Settings.TESTING:
            db_path = Settings.TESTING_DB_LOC
        else:
            db_path = Settings.DB_LOC"""

        if cls.path.is_file() is False:
            db_file = cls.path.open(mode="w+")
            db_file.close()

        cls.reset_db()

    @classmethod
    def reset_db(cls):
        with open(Settings.SCHEMA_LOC, "r") as script:
            db = DataManager.get_db()
            db.executescript(script.read().strip())

    @classmethod
    def get_db(cls):
        db = sqlite3.connect(DataManager.path, detect_types=sqlite3.PARSE_DECLTYPES)

        """if Settings.TESTING:
            db = sqlite3.connect(Settings.TESTING_DB_LOC, detect_types=sqlite3.PARSE_DECLTYPES)
        else:
            db = sqlite3.connect(Settings.DB_LOC, detect_types=sqlite3.PARSE_DECLTYPES)
"""
        db.row_factory = sqlite3.Row
        return db

    class GetData:
        def __init__(self, dm):
            self.db = dm.get_db()
            """if Settings.TESTING:
                self.db = dm.get_test_db()
            else:
                self.db = dm.get_db()"""

        def __enter__(self):
            return self.db

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.db.close()

    class StoreData:
        def __init__(self, dm):
            self.db = dm.get_db()
            """if Settings.TESTING:
                self.db = dm.get_test_db()
            else:
                self.db = dm.get_db()"""

        def __enter__(self):
            return self.db

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.db.commit()
            self.db.close()

    @classmethod
    def query(cls, query, single=False):
        with DataManager.GetData(cls) as db:
            try:
                conn = db.cursor()
                conn.execute(query)
                if single is True:
                    return conn.fetchone()
                else:
                    return conn.fetchall()
            except sqlite3.Error as e:
                print(f"An error occurred with the database: {e.args[0]}")

    @classmethod
    def _chain_filter_helper(cls, params, separator):
        # Goes through filtering AND params and returns a string of filtering AND statements to be used in a command
        filter_count = 0
        chain_where = ""

        for key, value in params.items():
            if type(value) is str:
                chain_where += f"{key}='{value}'"
            else:
                chain_where += f"{key}={value}"

            if filter_count != len(params.keys()) - 1:
                chain_where += separator

            filter_count += 1
        return chain_where

    @classmethod
    def to_obj(cls, db_result):
        program_obj = TrackedProgram.dict_init(db_result)
        if db_result is None:
            return None

        if program_obj.is_valid():
            return program_obj
        else:
            raise AttributeError("The program object from db was invalid")

    @classmethod
    def store_new(cls, program: Union[Program, TrackedProgram]):
        if program.is_valid():
            try:
                with cls.StoreData(cls) as db:
                    c = db.cursor()
                    command = f"INSERT INTO program_log (name, start_time, end_time, time_left, max_time) VALUES('{program.name}', {int(program.start_time)}, {int(program.end_time)}, {int(program.time_left)}, {int(program.max_time)}) "
                    c.execute(command)
            except sqlite3.Error as e:
                print(f"An error occurred with the database: {e.args[0]}")

    @classmethod
    def store_many(cls, *program_objs: TrackedProgram):
        query = f"INSERT INTO program_log (name, start_time, end_time, time_left, max_time) VALUES "
        rows = ""
        for program in program_objs:
            if program.is_valid():
                rows += f"('{program.name}', {int(program.start_time)}, {int(program.end_time)}, {int(program.time_left)}, {int(program.max_time)}),"
            else:
                raise AttributeError("TrackedProgram has an invalid attribute value")
        # removes ending comma from string
        rows = rows[0:len(rows) - 1]

        try:
            with cls.StoreData(cls) as db:
                c = db.cursor()
                c.execute(query + rows + ";")
        except sqlite3.Error as e:
            print(f"An error occurred with the database: {e.args[0]}")

    @classmethod
    def get(cls, **and_filters):
        if len(and_filters.keys()) == 0:
            return None

        query = f"SELECT * FROM program_log WHERE {cls._chain_filter_helper(and_filters, ' AND ')} LIMIT 1;"
        result = DataManager.query(query, single=True)
        return cls.to_obj(result)

    @classmethod
    def get_many(cls, limit=5, **query_params):
        query = "SELECT * FROM program_log"

        if len(query_params) != 0:
            query += f" WHERE {cls._chain_filter_helper(query_params, ' AND ')}"

        if limit is not None and type(limit) is int:
            query += f" LIMIT {limit};"
        elif limit is None:
            query += ";"
        else:
            return []

        program_objs = []
        results = cls.query(query, single=False)
        for row in results:
            program_objs.append(cls.to_obj(row))

        return program_objs

    @classmethod
    def update_pg(cls, pk, **values):
        # Check value isn't being updated
        if "id" in values.keys():
            del values['id']

        command = f"UPDATE program_log SET {cls._chain_filter_helper(values, ', ')} WHERE id={pk};"
        try:
            with cls.StoreData(cls) as db:
                conn = db.cursor()
                conn.execute(command)
        except sqlite3.Error as e:
            print(f"An error occurred with the database: {e.args[0]}")

    @classmethod
    def id_of_obj(cls, program):
        obj = cls.get(start_time=program.start_time, name=program.name)
        if obj is not None:
            return obj.db_id

    @classmethod
    def get_date_range(cls, start: datetime, end: datetime, limit=5, **query_params):
        epoch_time1 = start.timestamp()
        epoch_time2 = end.timestamp()

        query = ""
        if len(query_params.keys()) != 0:
            query = f"SELECT * FROM program_log WHERE start_time >= {epoch_time1} AND end_time <= {epoch_time2} AND {cls._chain_filter_helper(query_params, ' AND ')}"
        else:
            query = f"SELECT * FROM program_log WHERE start_time >= {epoch_time1} AND start_time <= {epoch_time2}"

        if limit is not None and limit is int:
            query += f" LIMIT {limit};"
        else:
            query += ";"

        programs = []
        results = cls.query(query, single=False)
        if results is not None:
            for row in results:
                programs.append(cls.to_obj(row))

            return programs
        else:
            return []

    @classmethod
    def get_day(cls, day, limit=5, **query_params):
        start = datetime(day.year, day.month, day.day)
        end = start + timedelta(hours=23, minutes=59, seconds=59)

        return cls.get_date_range(start, end, limit, **query_params)

    @classmethod
    def log_ended(cls, log_end):
        for item in log_end:
            last_save = item.get_latest_save()
            assert last_save is not None, "Tried to end a running game with no save"

            cls.update_pg(cls.id_of_obj(last_save), end_time=item.end_time, time_remaining=item.time_left())


class StateChangeDetector:
    def __init__(self):
        self.prev_state = []
        self.curr_state = []

    def update_states(self, pruned_pgs):
        self.prev_state = self.curr_state
        self.curr_state = pruned_pgs

    def is_stopped(self, new_pg_state):
        old_pg_state = Program.get_program(new_pg_state, self.prev_state)
        new_pg_state = Program.get_program(new_pg_state, self.curr_state)

        # If old state is found, means it was running, if new state is not found that means its not running anymore
        return old_pg_state is not None and new_pg_state is None

    def is_started(self, new_state):
        old_state = Program.get_program(new_state, self.prev_state)
        new_state = Program.get_program(new_state, self.curr_state)
        return old_state is None and new_state is not None

    def get_started(self):
        started_pgs = []
        for item in self.curr_state:
            if self.is_started(item):
                started_pgs.append(item)

        # Expects prev_logged_save to take care of logic to load previously saved programs
        started_pgs = LoadData.prev_logged_save(started_pgs)
        return started_pgs

    def get_stopped(self):
        ended_pgs = []
        for item in self.prev_state:
            if self.is_stopped(item):
                ended_pgs.append(item)
        return ended_pgs


class StateLogger:

    def __init__(self, program_states):
        self.program_states = program_state

    def log_started(self, to_log):
        self.set_starts(to_log)
        DataManager.store_many(*to_log)

    def log_end(self, to_log):
        self.set_ends(to_log)
        DataManager.log_ended(to_log)

    def set_starts(self, items):
        for item in items:
            item.start_now()

    def set_ends(self, items):
        for item in items:
            item.end_now()


class ProgramManager:

    def __init__(self, ps):
        self.PS: ProgramStates = ps
        self.blocked_programs = []

    def kill(self, program):
        for pid in program.PIDS:
            try:
                psutil.Process(pid).kill()
            except psutil.NoSuchProcess:
                pass
        program.reset_pids()

    def update_blocked(self):
        for program in self.PS.program_objs:
            if self.is_blocked(program):
                self.add_to_blocked(program)

    def add_to_blocked(self, pg):
        in_blocked_arr = Program.get_program(pg, self.blocked_programs) is not None
        if self.is_blocked(pg) and in_blocked_arr is False:
            # Values are updated to ensure they are consistent with each other
            pg.blocked = True
            pg.time_left = 0
            self.blocked_programs.append(pg)

    def is_blocked(self, program):
        in_blocked_arr = Program.get_program(program, self.blocked_programs) is not None

        return in_blocked_arr or program.blocked or program.time_left == 0

    def prune_programs(self, not_checked_programs):
        """
        Is passed in a list of program objects and iterates through to check for any blocked. If a blocked object is
        found, it is stopped and added to the blocked array if not already in it. It then returns all the programs that
        were not blocked
        """
        checked_pgs = []
        for program in not_checked_programs:
            if self.is_blocked(program):
                self.add_to_blocked(program)
                self.kill(program)
            else:
                checked_pgs.append(program)

        return checked_pgs


class ProgramStates:
    def __init__(self):
        self.currently_running = []
        self.program_objs = []
        self.init_program_objs()

    def get_program(self, pg):
        for program in self.program_objs:
            if pg.name == program.name:
                return program
        return None

    def update_elapsed(self):
        for pg in self.currently_running:
            pg.elapsed_time += self.get_loop_time()

    def get_loop_time(self):
        return Settings.LOOP_TIME

    def reset(self):
        # Resets the PIDS of the program objects and removes all from currently running
        self.currently_running = []
        for pg in self.program_objs:
            pg.PIDS = []

    def tracked_from_settings(self):
        programs = []
        for program in Settings.TRACKED_PROGRAMS:
            programs.append(Program.min_init(program[0], program[1]))
        return programs

    def init_program_objs(self):
        for program in LoadData.saves_program_init(self.tracked_from_settings()):
            pg_obj = Program(program)
            if pg_obj.time_left == 0:
                pg_obj.blocked = True
            self.program_objs.append(pg_obj)

    def populate_program_pids(self):
        # iterate through processes
        for process in psutil.process_iter(attrs=['name', 'pid']):
            process_name = process.info['name'].lower()

            for program in self.program_objs:

                if program.name.lower() in process_name:
                    pid = process.info['pid']
                    program.add_pid(pid)

    def add_to_running(self):
        for pg in self.program_objs:
            if pg.is_running():
                self.currently_running.append(pg)

    def get_curr_running(self):
        self.reset()
        self.populate_program_pids()
        self.add_to_running()
        return self.currently_running


class LoadData:
    # Gets initial states for program
    @classmethod
    def saves_program_init(cls, programs):
        saves = []
        for pg in programs:
            loaded = pg.get_latest_save()
            # If there is no save return the original object

            if loaded is None:
                saves.append(pg)
            else:
                loaded.end_time = 0
                loaded.start_time = 0
                saves.append(loaded)

        return saves

    @classmethod
    def prev_logged_save(cls, programs):
        saves = []
        for pg in programs:
            loaded = pg.get_latest_save()

            # If there is no save return the original object
            if loaded is None:
                saves.append(pg)
            else:
                if loaded.time_left < pg.time_left:
                    pg.time_left = loaded.time_left
                saves.append(pg)

        return saves


if __name__ == '__main__':
    # Start the db with the right schema
    # Reset any data that is in the db
    DataManager.init_db()
    # DataManager.reset_db()
    # DataManager.store_new(TrackedProgram("Chrome", 10, time.time()-5, time.time(), 5))
    # DataManager.store_new(TrackedProgram("Chrome", 10, time.time(), time.time()+4, 1))

    program_state = ProgramStates()

    # Init state detector which keeps track of what programs have just been started or stopped (no saves needed)
    state_detector = StateChangeDetector()

    # Deals with the ending of programs, filtering and blocking (needs access to pg objs from currently running)
    program_manager = ProgramManager(program_state)

    # Class for all others to access and get currently running/program objs (needs saves to be loaded)
    program_manager.update_blocked()
    logger = StateLogger(program_state)

    while True:
        # Removes programs that shouldn't be running
        running = program_state.get_curr_running()
        print(str([pg.name for pg in running]))
        pruned = program_manager.prune_programs(running)

        # State detector gets which programs should be updated
        state_detector.update_states(pruned)
        started = state_detector.get_started()
        ended = state_detector.get_stopped()

        # Logger keeps ProgramStates and DB with most current info
        logger.log_end(ended)
        logger.log_started(started)

        # Update program manager with
        program_state.update_elapsed()
        program_manager.update_blocked()
        time.sleep(Settings.LOOP_TIME)

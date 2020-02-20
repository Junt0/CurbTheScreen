import os
import sqlite3
import time
from datetime import datetime, timedelta
import psutil

# Is a stripped down program object to differentiate between running programs and given programs to track
import Settings


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
                setattr(program, f"db_{key}", attrs[key])
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

        if self.start_time == 0 and self.end_time == 0 and self._time_left == 0:
            left = self.max_time
        elif self.start_time != 0 and (self.end_time == 0 or self.end_time != 0):
            if self._time_left == 0:
                left = 0
            else:
                left = self._time_left - self.elapsed_time

        """if self.start_time == 0 and self.end_time == 0:
            left = self.max_time
        elif self.start_time != 0 and self.end_time == 0:
            left = int(self._time_left - self.elapsed_time)
        elif self.start_time != 0 and self.end_time != 0:
            left = int(self._time_left - self.elapsed_time)

        if left < 0:
            left = 0

        self._time_left = left
        return self._time_left"""
        self._start_time = left
        return self._start_time

    @time_left.setter
    def time_left(self, value):
        if self._is_float_or_int_not_neg(value):
            self._time_left = float(value)
        else:
            raise ValueError("Invalid value assigned to time_left")

    def start_now(self):
        self.start_time = int(time.time())

    def end_now(self):
        self.end_time = int(time.time())

    def update(self, program_obj):
        if self.start_time == 0:
            self.start_time = program_obj.start_time

        if self.end_time == 0:
            self.end_time = program_obj.end_time

        self.time_left = program_obj.time_left

    def is_valid(self):
        num_vars = [self.start_time, self.end_time, self._time_left]

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
        return is_str

    def _is_float_or_int_not_neg(self, value):
        right_type = self._is_float(value) or self._is_int(value)

        right_sign = False
        if right_type:
            right_sign = self._is_negative(value)

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
        return value >= 0

    def _is_none(self, value):
        return value is None

    def _is_db_id_valid(self):
        # TODO check if id exists in db
        pass

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

        return blocked_equal and name_equal and start_time_equal and end_time_equal and max_time_equal


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


# Stores any changes made into the database
class DataManager:

    @classmethod
    def init_db(cls):
        db_path = ""
        if Settings.TESTING:
            db_path = Settings.TESTING_DB_LOC
        else:
            db_path = Settings.DB_LOC

        if os.path.isfile(db_path) is False:
            db_file = open(db_path, "w+")
            db_file.close()

        cls.reset_db()

    @classmethod
    def reset_db(cls):
        with open(Settings.SCHEMA_LOC, "r") as script:
            db = DataManager.get_db()
            db.executescript(script.read().strip())

    @classmethod
    def get_db(cls):
        db = None

        if Settings.TESTING:
            db = sqlite3.connect(Settings.TESTING_DB_LOC, detect_types=sqlite3.PARSE_DECLTYPES)
        else:
            db = sqlite3.connect(Settings.DB_LOC, detect_types=sqlite3.PARSE_DECLTYPES)

        db.row_factory = sqlite3.Row
        return db

    class GetData:
        def __init__(self, dm):
            if Settings.TESTING:
                self.db = dm.get_test_db()
            else:
                self.db = dm.get_db()

        def __enter__(self):
            return self.db

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.db.close()

    class StoreData:
        def __init__(self, dm):
            if Settings.TESTING:
                self.db = dm.get_test_db()
            else:
                self.db = dm.get_db()

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
    def to_obj(cls, db_result):
        program_obj = TrackedProgram.dict_init(db_result)
        if db_result is None:
            return None

        if program_obj.is_valid():
            return program_obj
        else:
            raise Exception("The program object was invalid!")

    @classmethod
    def chain_and_helper(cls, params):
        # Goes through filtering params and adds them to the chain
        filter_count = 0
        chain_where = ""

        for key, value in params.items():
            if type(value) is str:
                chain_where += f"{key}='{value}'"
            else:
                chain_where += f"{key}={value}"

            if filter_count != len(params.keys()) - 1:
                chain_where += " AND "

            filter_count += 1
        return chain_where

    @classmethod
    def get(cls, **query_params):
        if len(query_params.keys()) == 0:
            return None

        query = f"SELECT * FROM program_log WHERE {cls.chain_and_helper(query_params)} LIMIT 1;"
        result = DataManager.query(query, single=True)
        return cls.to_obj(result)

    @classmethod
    def update_pg(cls, id, **values):
        set_vals = ""
        count = 0
        for key, value in values.items():
            if type(value) is str:
                set_vals += f"{key}='{value}'"
            else:
                set_vals += f"{key}={value}"

            if count != len(values.keys()) - 1:
                set_vals += ", "

            count += 1

        command = f"UPDATE program_log SET {set_vals} WHERE id={id};"
        try:
            with cls.StoreData(cls) as db:
                conn = db.cursor()
                conn.execute(command)
        except sqlite3.Error as e:
            print(f"An error occurred with the database: {e.args[0]}")

    @classmethod
    def store_new(cls, program):
        if isinstance(program, Program) or isinstance(program, TrackedProgram):
            if program.is_valid():
                try:
                    with cls.StoreData(cls) as db:
                        c = db.cursor()
                        command = f"INSERT INTO program_log (name, start_time, end_time, time_remaining, max_time) VALUES('{program.name}', {int(program.start_time)}, {int(program.end_time)}, {int(program.__time_remaining)}, {int(program.max_time)})"
                        c.execute(command)
                except sqlite3.Error as e:
                    print(f"An error occurred with the database: {e.args[0]}")

    @classmethod
    def store_many(cls, *program_objs):
        query = f"INSERT INTO program_log (name, start_time, end_time, time_remaining, max_time) VALUES "
        rows = ""
        for program in program_objs:
            if isinstance(program, Program) or isinstance(program, TrackedProgram):
                if program.is_valid():
                    rows += f"('{program.name}', {int(program.start_time)}, {int(program.end_time)}, {int(program.__time_remaining)}, {int(program.max_time)}),"
                else:
                    raise Exception("The game object put in was not valid!")
        # removes ending comma
        rows = rows[0:len(rows) - 1]

        try:
            with cls.StoreData(cls) as db:
                c = db.cursor()
                c.execute(query + rows + ";")
        except sqlite3.Error as e:
            print(f"An error occurred with the database: {e.args[0]}")

    @classmethod
    def id_of_obj(cls, program):
        obj = cls.get(start_time=program.start_time, name=program.name)
        if obj is not None:
            return obj.db_id

    @classmethod
    def get_many(cls, limit=5, **query_params):
        query = "SELECT * FROM program_log"

        if len(query_params) != 0:
            query += f" WHERE {cls.chain_and_helper(query_params)}"

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
    def get_date_range(cls, start, end, limit=5, **query_params):
        epoch1 = start.timestamp()
        epoch2 = end.timestamp()

        query = ""
        if len(query_params.keys()) != 0:
            query = f"SELECT * FROM program_log WHERE start_time >= {epoch1} AND end_time <= {epoch2} AND {cls.chain_and_helper(query_params)}"
        else:
            query = f"SELECT * FROM program_log WHERE start_time >= {epoch1} AND start_time <= {epoch2}"

        if limit is not None and limit is int:
            query += f" LIMIT {limit};"
        else:
            query += f";"

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
        end = start + timedelta(hours=24)

        return cls.get_date_range(start, end, limit, **query_params)

    # store tracked program data
    @classmethod
    def log_started(cls, log_start):
        for item in log_start:
            cls.store_new(item)

    @classmethod
    def log_ended(cls, log_end):
        for item in log_end:
            last_save = item.get_latest_save()
            cls.update_pg(cls.id_of_obj(last_save), end_time=item.end_time, time_remaining=item.time_left())


class StateChangeDetector:
    def __init__(self, ps):
        self.PS: ProgramStates = ps
        self.prev_state = []
        self.curr_state = []

    def update_states(self, pruned_pgs):
        self.prev_state = self.curr_state
        self.curr_state = pruned_pgs

    def get_program(self, program, array):
        for item in array:
            if program.name == item.name:
                return item
        return None

    def is_stopped(self, new_state):
        old_state = self.get_program(new_state, self.prev_state)
        new_state = self.get_program(new_state, self.curr_state)

        # If old state is found, means it was running, if new state is not found that means its not running anymore
        return old_state is not None and new_state is None

    def is_started(self, new_state):
        old_state = self.get_program(new_state, self.prev_state)
        new_state = self.get_program(new_state, self.curr_state)
        return old_state is None and new_state is not None

    def get_started(self):
        started_pgs = []
        for item in self.curr_state:
            if self.is_started(item):
                if item.has_save():
                    save = item.get_latest_save()
                    if save is not None:
                        if save.time_remaining < item.time_remaining:
                            item.time_remaining = save.time_remaining
                item.elapsed_time = 0
                started_pgs.append(item)
        return started_pgs

    def get_stopped(self):
        ended_pgs = []
        for item in self.prev_state:
            if self.is_stopped(item):
                ended_pgs.append(item)
        return ended_pgs


class StateLogger:
    program_states = None

    def __init__(self, program_states):
        self.program_states = program_state

    def log_started(self, to_log):
        self.set_starts(to_log)
        DataManager.log_started(to_log)

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

    def get_program(self, program, array):
        for item in array:
            if program.name == item.name:
                return item
        return None

    def update_blocked(self):
        self.blocked_programs = self.PS.update_blocked()

    def add_to_blocked(self, pg):
        blocked = self.get_program(pg, self.blocked_programs)
        if blocked is None:
            blocked.blocked = True
            self.blocked_programs.append(blocked)

    def is_blocked(self, program):
        return program in self.blocked_programs or program.blocked

    def prune_programs(self, unclean_running):
        cleaned_running = []
        for program in unclean_running:
            pg = self.get_program(program, self.blocked_programs)
            if pg is None:
                cleaned_running.append(program)
                continue

            if self.is_blocked(pg):
                self.kill(program)
            else:
                cleaned_running.append(program)

        return cleaned_running


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
            pg.elapsed_time += Settings.LOOP_TIME

    def update_blocked(self):
        blocked = []

        for program in self.program_objs:
            time_left = program.time_left()
            if time_left == 0 or program.blocked:
                program.blocked = True
                program.time_remaining = program.time_left()
                blocked.append(program)

        return blocked

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
        for program in self.tracked_from_settings():
            pg_obj = Program(program)

            # Gets the latest save that is available and if it has less time remaining update the old save
            if pg_obj.has_save():
                save: TrackedProgram = pg_obj.get_latest_save()
                if save is not None:
                    pg_obj.__time_remaining = save.__time_remaining

                    if pg_obj.__time_remaining == 0:
                        pg_obj.blocked = True
                    else:
                        pg_obj.blocked = False

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
    @classmethod
    def program_states(cls, programs):
        saves = []
        for pg in programs:
            loaded = pg.get_latest_save()
            if loaded is None:
                saves.append(pg)
            else:
                loaded.end_time = 0
                loaded.start_time = 0
                saves.append(loaded)

        return saves

    # Loads initial states for program


if __name__ == '__main__':
    # Start the db with the right schema
    # Reset any data that is in the db
    DataManager.init_db()
    # DataManager.reset_db()
    # DataManager.store_new(TrackedProgram("Chrome", 10, time.time()-5, time.time(), 5))
    # DataManager.store_new(TrackedProgram("Chrome", 10, time.time(), time.time()+4, 1))

    program_state = ProgramStates()

    # Init state detector which keeps track of what programs have just been started or stopped (no saves needed)
    state_detector = StateChangeDetector(program_state)

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

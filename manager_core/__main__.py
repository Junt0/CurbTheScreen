import time

import manager_core.SettingsParser as SettingsParser
from manager_core.CurbTheScreen import DataManager, ProgramStates, StateChangeDetector, ProgramManager, StateLogger


def init_classes():
    root_dir_name = SettingsParser.settings.root_dir_name
    root_dir = SettingsParser.settings.get_base_loc(root_dir_name)

    DataManager.init_db(root_dir)
    # DataManager.reset_db()

    program_state = ProgramStates()

    # Init state detector which keeps track of what programs have just been started or stopped (no saves needed)
    state_detector = StateChangeDetector()

    # Deals with the ending of programs, filtering and blocking (needs access to pg objs from currently running)
    program_manager = ProgramManager(program_state)
    # Class for all others to access and get currently running/program objs (needs saves to be loaded)
    program_manager.update_blocked()

    logger = StateLogger(program_state)

    return logger, program_state, state_detector, program_manager


def run():
    # Start the db with the right schema
    # Reset any data that is in the db
    SettingsParser.settings.reload_cache()

    logger, program_state, state_detector, program_manager = init_classes()

    # Before the program is shutdown, currently running programs are updated
    import atexit
    atexit.register(DataManager.save_state, program_state, program_manager, state_detector)

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
        time.sleep(SettingsParser.settings.get_attr("LOOP_TIME"))


if __name__ == '__main__':
    run()

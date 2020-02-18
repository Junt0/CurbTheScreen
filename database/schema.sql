DROP TABLE IF EXISTS program_log;

CREATE TABLE program_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_time INTEGER NOT NULL,
    end_time INTEGER NOT NULL,
    time_remaining INTEGER NOT NULL,
    max_time INTEGER NOT NULL
);
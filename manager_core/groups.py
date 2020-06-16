from abc import ABC, abstractmethod
from typing import Union, List

"""
class SettingsChunk:

    def __init__(self, config: dict, required: list=[], optional: list=[], chunks: List[SettingsChunk] = []):
        self.required_settings = required
        self.optional_settings = optional
        self.parsers = {}
        self.cached_config = {}

    def add_parser(self, func):
        @functools.wraps(func)
        def parser():
            self.parsers[func.__name__] = func
            return func

        return parser()

    def get_attr(self, setting):
        if not self._is_in_config(setting):
            return self._get_optional_default(setting)

        setting_value = self.cached_config[setting]
        if setting in self.parsers.keys():
            func = self._get_parser(setting)
            return func(setting_value)

        return setting_value

    def _get_optional_default(self, setting):
        for values in self.optional_settings:
            name = values[0]

            if setting == name:
                default_val = values[1]
                return default_val
        raise LookupError(f"{setting} did not have a value associated with it")

    def _get_optional_names(self):
        return [setting[0] for setting in self.optional_settings]

    def _is_optional(self, setting):
        try:
            self._get_optional_default(setting)
            return True
        except LookupError as e:
            return False

    def _is_setting_defined(self, setting):
        # setting is in either optional or required
        return setting in self._all_setting_names()

    def _is_in_config(self, setting):
        return setting in self.cached_config.keys()

    def _all_setting_names(self):
        return self.required_settings + self._get_optional_names()

    def _get_parser(self, setting):
        parse_func = self.parsers[setting]
        return parse_func

    # TODO update the main settings class which then updates the whole thing
    def update_config(self):
        pass
    
    # TODO make the main settings class update and load in the chunk
    def reload_cache(self):
        pass

    def update_setting(self, setting, value):
        if setting in self._all_setting_names():
            self.cached_config[setting] = value
        else:
            raise LookupError(f"{setting} did not have a value associated with it")
"""


class Parser:
    def __init__(self, name):
        self.settings = settings
        self.name = name

    def is_valid(self, settings):
        return True


class Settings:
    def __init__(self, parsers, chunks, settings):
        self.parsers = parsers
        self.chunks = chunks
        self.settings = settings

    def is_valid(self):
        for parser in self.parsers:
            if not temp_parser.is_valid(self.settings):
                return False

        for chunk in chunks:
            if not chunk.is_valid(self.settings):
                return False


class SettingsRetrieval:
    def __init__(self, cached_config, parsers, required=[], optional=[]):
        self.cached_config = cached_config
        self.parsers = parsers
        self.required = required
        self.optional = optional

    @classmethod
    def from_settings_chunk(cls, chunk, chunk_dict):
        return MatchedChunk(chunk_dict, chunk.name, chunk.parsers, chunk.chunks, chunk.required, chunk.optional)

    def get_attr(self, setting):
        if not self._is_in_chunk(setting):
            return self._get_optional_default(setting)

        setting_value = self.cached_config[setting]
        if setting in self.parsers.keys():
            func = self._get_parser(setting)
            return func(setting_value)

        return setting_value

    def _get_optional_default(self, setting):
        for values in self.optional_settings:
            name = values[0]

            if setting == name:
                default_val = values[1]
                return default_val
        raise LookupError(f"{setting} did not have a value associated with it")

    def _get_optional_names(self):
        return [setting[0] for setting in self.optional_settings]

    def _is_optional(self, setting):
        try:
            self._get_optional_default(setting)
            return True
        except LookupError as e:
            return False

    def _is_setting_defined(self, setting):
        # setting is in either optional or required
        return setting in self._all_setting_names()

    def _is_in_chunk(self, setting):
        return setting in self.matched_chunk.keys()

    def _all_setting_names(self):
        return self.required_settings + self._get_optional_names()

    # TODO refactor to use the class parsers
    def _get_parser(self, setting):
        parse_func = self.parsers[setting]
        return parse_func

    def update_setting(self, setting, value):
        if setting in self._all_setting_names():
            self.cached_config[setting] = value
        else:
            raise LookupError(f"{setting} did not have a value associated with it")


class SettingsChunk:
    def __init__(self, name, parsers, chunks=[], required=[], optional=[]):
        self.retrieval: SettingsRetrieval = None
        self.name = name
        self.chunks = chunks
        self.matched_chunks = []

    def check_dict(self, settings: dict):
        self.retrieval = SettingsRetrieval(self.settings_dict, self.parsers, self.required, self.optional)

    def is_valid(self, settings):
        settings_part = settings[self.name]
        for parser in self.parsers:
            temp_parser = parser(settings_part)
            if not temp_parser.is_valid():
                return False

        for chunk in self.chunks:
            if not chunk.is_valid(settings_part):
                return False


class ChunkTemplate(SettingsChunk):
    def __init__(self, chunk_type, parsers, chunks=[], required=[], optional=[]):
        self.chunk_type = chunk_type
        super().__init__("", parsers, chunks=chunks + ['TYPE'], required=required, optional=optional)

    def find_matches(self, settings):
        matches = []

        for key in settings.keys():
            self.check_dict(settings[key])

            for chunk in self.chunks:

                try:
                    chunk_type = self.retrieval.get_attr("TYPE")
                    if chunk_type == self.chunk_type:
                        matches.append(self.to_settings_chunk(key))
                except:
                    continue

        return matches

    def to_settings_chunk(self, name):
        return SettingsChunk(name, self.parsers, self.chunks, self.required, self.optional)

    def is_valid(self, settings_part):
        matches = self.find_matches(settings_part)
        for match in matches:
            if not match.is_valid():
                return False
        return True

    my_settings = Settings(
        # parsers need to have the attribute with their name passed in
        parsers=[Parser("ROOT_DIR_NAME"), Parser("LOOP_TIME")],  # DirName, LoopTime],

        chunks=[
            SettingsChunk(
                name="GROUPS",
                chunks=[
                    ChunkTemplate(
                        chunk_type="default",
                        required=['TRACKED_PROGRAMS'],
                        parsers=[Parser("TYPE")],  # DefaultProgramParser],
                        # parsed_class=DefaultGroup
                    ),
                    ChunkTemplate(
                        chunk_type="totaltime",
                        required=['TRACKED_PROGRAMS', 'TOTAL_TIME'],
                        parsers=[Parser("TYPE"), Parser("TotalTime")],  # CombinedProgramParser, TotalTime],
                        # parsed_class=TotalTimeGroup
                    )
                ]
            )
        ]

    )

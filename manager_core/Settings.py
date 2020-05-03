import functools
import json
import os
from pathlib import Path


class Settings:
    root_dir_name = "CurbTheScreen"
    location = None
    is_build = False

    def __init__(self, required: list, optional: list):
        self.required_settings = required
        self.optional_settings = optional
        self.parsers = {}
        self.cached_config = {}

    @classmethod
    def get_base_loc(cls, dir_name) -> Path:
        cur_dir_path = Path(os.getcwd())
        try:
            index = cur_dir_path.parts.index(dir_name)
        except ValueError:
            return None

        p = ""
        for part in range(0, index + 1):
            if part == 0:
                p += "/"
            else:
                p += f'{cur_dir_path.parts[part]}/'

        return Path(p)

    def add_parser(self, func):
        @functools.wraps(func)
        def parser():
            self.parsers[func.__name__] = func
            return func

        return parser()

    def get_attr(self, setting):
        if not self._is_in_file(setting):
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

    def _is_in_file(self, setting):
        return setting in self.cached_config.keys()

    def _all_setting_names(self):
        return self.required_settings + self._get_optional_names()

    def _get_parser(self, setting):
        parse_func = self.parsers[setting]
        return parse_func

    def update_config(self):
        with open(self.location, 'w') as json_file:
            json.dump(self.cached_config, json_file, indent=4)

    def reload_cache(self):
        with open(self.location) as f:
            self.cached_config = json.load(f)

    def update_setting(self, setting, value):
        if setting in self._all_setting_names():
            self.cached_config[setting] = value
        else:
            raise LookupError(f"{setting} did not have a value associated with it")

    def update_setting_reload(self, setting, value):
        self.update_setting(setting, value)
        self.update_config()

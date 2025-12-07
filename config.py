import configparser
import os
from pathlib import Path

class AppConfig:
    def __init__(self, config_path):
        self._config = configparser.ConfigParser()
        self._config_path = Path(config_path)
        if not self._config_path.is_file():
            raise FileNotFoundError(f"Config file not found at: {self._config_path}")
        self._config.read(self._config_path)

    def get_board_url(self, board_number):
        try:
            board_id = self._config.get("boards", f"board{board_number}_id")
            return f"https://play.autodarts.io/boards/{board_id}/follow"
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None

    @property
    def use_custom_style(self):
        return self._config.getboolean("style", "activate", fallback=False)

    @property
    def browser_count(self):
        return self._config.getint("main", "browsers", fallback=1)

    @property
    def cache_dir(self):
        return self._config.get("main", "cachedir", fallback="_cache/")

    @property
    def logos_enabled(self):
        return self._config.getboolean("logos", "enable", fallback=False)

    @property
    def logos_local(self):
        return self._config.getboolean("logos", "local", fallback=False)

    @property
    def logo_source(self):
        return self._config.get("logos", "logo", fallback="")

    @property
    def autologin_enabled(self):
        return self._config.getboolean("autologin", "enable", fallback=False)

    @property
    def autologin_max_attempts(self):
        return self._config.getint("autologin", "versuche", fallback=3)

    @property
    def autologin_username(self):
        return self._config.get("autologin", "username", fallback="")

    @property
    def autologin_password(self):
        return self._config.get("autologin", "passwort", fallback="")

def get_config():
    working_path = Path(__file__).parent
    config_file = working_path / "config.ini"
    return AppConfig(config_file)

import configparser
import os
import uuid
from pathlib import Path
from utils import CONFIG_PATH, decrypt_value

class AppConfig:
    def __init__(self, config_path=CONFIG_PATH):
        # Allow # in values by restricting comment prefixes to ;
        self._config = configparser.ConfigParser(comment_prefixes=';', inline_comment_prefixes=';')
        self._config_path = Path(config_path)
        # If file exists, read it. If not, we just have an empty config which returns fallbacks.
        if self._config_path.is_file():
            self._config.read(self._config_path)

        # Ensure device_id exists
        if not self._config.has_section("main"):
            self._config.add_section("main")
        
        if not self._config.has_option("main", "device_id"):
            # Generate a new UUID if not present
            new_id = str(uuid.uuid4())
            self._config.set("main", "device_id", new_id)
            # Save immediately so the ID persists
            self.save()

    def save(self):
        """Saves the current configuration to the file."""
        with open(self._config_path, 'w') as f:
            self._config.write(f)

    def set(self, section, option, value):
        """Sets a configuration value, creating the section if needed."""
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, option, str(value))

    # --- Read Accessors ---

    def get_board_url(self, board_number):
        try:
            board_id = self._config.get("boards", f"board{board_number}_id")
            return f"https://play.autodarts.io/boards/{board_id}/follow"
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None

    @property
    def device_id(self):
        return self._config.get("main", "device_id")

    @property
    def device_name(self):
        return self._config.get("main", "device_name", fallback="")

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
        # Prefer 'attempts', fallback to 'versuche' for backward compatibility
        return self._config.getint("autologin", "attempts", 
                                  fallback=self._config.getint("autologin", "versuche", fallback=3))

    @property
    def autologin_username(self):
        return self._config.get("autologin", "username", fallback="")

    @property
    def autologin_password(self):
        # Try 'password' first
        val = self._config.get("autologin", "password", fallback=None)
        # If not found or empty, try legacy 'passwort'
        if not val:
            val = self._config.get("autologin", "passwort", fallback="")
        
        # Decrypt the value (returns plaintext if it wasn't encrypted)
        return decrypt_value(val)

    @property
    def refresh_interval_min(self):
        return self._config.getint("main", "refresh_interval_min", fallback=0)

    @property
    def zoom_factor(self):
        try:
            return self._config.getfloat("main", "zoom_factor", fallback=1.0)
        except ValueError:
            return 1.0

    @property
    def screen(self):
        return self._config.getint("main", "screen", fallback=0)

    @property
    def web_auth_enabled(self):
        return self._config.getboolean("security", "enable_auth", fallback=False)

    @property
    def web_username(self):
        return self._config.get("security", "username", fallback="admin")

    @property
    def web_password_hash(self):
        return self._config.get("security", "password_hash", fallback="")
    
    @property
    def auto_coords_mode(self):
        return self._config.getboolean("style", "auto_coords_mode", fallback=False)
    
    # --- Raw Access for Form Population ---
    # Used by config_server to populate forms, allowing us to get raw values or defaults
    def get(self, section, option, fallback=None):
        return self._config.get(section, option, fallback=fallback)
    
    def getint(self, section, option, fallback=None):
        return self._config.getint(section, option, fallback=fallback)
    
    def getboolean(self, section, option, fallback=None):
        return self._config.getboolean(section, option, fallback=fallback)
        
    def getfloat(self, section, option, fallback=None):
        return self._config.getfloat(section, option, fallback=fallback)

    def has_section(self, section):
        return self._config.has_section(section)

    def add_section(self, section):
        self._config.add_section(section)

def get_config():
    return AppConfig(CONFIG_PATH)
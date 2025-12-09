import os
import time
import threading
from pathlib import Path

# --- Constants & Paths ---
APP_DIR = Path(__file__).parent
CONFIG_PATH = APP_DIR / "config.ini"
CSS_PATH = APP_DIR / "style.css"
THEMES_DIR = APP_DIR / "themes"
SCRIPTS_DIR = APP_DIR / "scripts"
TEMPLATES_DIR = APP_DIR / "templates"

# Trigger Files
RESTART_TRIGGER_PATH = APP_DIR / ".restart_trigger"
RELOAD_TRIGGER_PATH = APP_DIR / ".reload_trigger"
CLEAR_CACHE_MARKER_PATH = APP_DIR / ".clear_cache"

# Logging
LOG_DIR = APP_DIR / "logs"
LOG_PATH = LOG_DIR / "adarts-browser.log"

if not LOG_DIR.exists():
    LOG_DIR.mkdir()

def touch_trigger_file(path, delay=0.0):
    """Touches a trigger file, optionally after a delay (in a separate thread)."""
    def _touch():
        if delay > 0:
            time.sleep(delay)
        try:
            if not path.exists():
                path.touch()
            os.utime(path, None)
        except OSError:
            pass

    if delay > 0:
        threading.Thread(target=_touch, daemon=True).start()
    else:
        _touch()

def trigger_restart(delay=1.0):
    """Triggers an application restart."""
    touch_trigger_file(RESTART_TRIGGER_PATH, delay)

def trigger_reload(delay=0.5):
    """Triggers a page reload."""
    touch_trigger_file(RELOAD_TRIGGER_PATH, delay)

def request_clear_cache():
    """Creates the marker file to request cache clearing on restart."""
    try:
        CLEAR_CACHE_MARKER_PATH.touch()
        trigger_restart()
        return True
    except Exception:
        return False

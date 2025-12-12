import os
import time
import threading
import socket
import netifaces
import qrcode
import subprocess
import json
import urllib.request
from urllib.parse import quote
from io import BytesIO
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

# --- Constants & Paths ---
APP_DIR = Path(__file__).parent
CONFIG_PATH = APP_DIR / "config.ini"
KEY_PATH = APP_DIR / ".secret.key"
CSS_PATH = APP_DIR / "style.css"
THEMES_DIR = APP_DIR / "themes"
SCRIPTS_DIR = APP_DIR / "scripts"
TEMPLATES_DIR = APP_DIR / "templates"

THEME_REPO_BASE_URL = "https://raw.githubusercontent.com/mluckau/adarts-browser-themes/main/"

# Trigger Files
RESTART_TRIGGER_PATH = APP_DIR / ".restart_trigger"
RELOAD_TRIGGER_PATH = APP_DIR / ".reload_trigger"
CLEAR_CACHE_MARKER_PATH = APP_DIR / ".clear_cache"

# Logging
LOG_DIR = APP_DIR / "logs"
LOG_PATH = LOG_DIR / "adarts-browser.log"

if not LOG_DIR.exists():
    LOG_DIR.mkdir()

# --- Network & QR Helpers ---
def get_local_ip_address():
    """
    Attempts to find the primary local IP address of the device.
    Prioritizes non-localhost, non-loopback IPv4 addresses.
    """
    try:
        # Strategy 1: Connect to an external server (Google DNS) - most reliable
        # We don't actually send data, just checking what IP would be used
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
            return ip
        except Exception:
            pass
        finally:
            s.close()

        # Strategy 2: Iterate interfaces using netifaces
        for interface in netifaces.interfaces():
            if interface == 'lo':
                continue
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr_info in addrs[netifaces.AF_INET]:
                    ip = addr_info['addr']
                    if not ip.startswith('127.'):
                        return ip
    except Exception:
        pass
    
    return "127.0.0.1"

def generate_qr_code_image(data):
    """
    Generates a QR code for the given data and returns it as a bytes object (PNG).
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    return img_buffer.getvalue()

# --- Theme Repository Helpers ---
def fetch_available_themes():
    """Fetches the list of themes from the online repository (themes.json)."""
    # Add timestamp to bypass caching
    url = THEME_REPO_BASE_URL + f"themes.json?v={int(time.time())}"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        # Return empty list on error (offline, repo not found, etc.)
        print(f"[WARN] Failed to fetch online themes: {e}")
        return []

def fetch_theme_content(filename):
    """Fetches the content of a specific css file from the online repository."""
    # Ensure filename is URL encoded (handles spaces etc.)
    encoded_filename = quote(filename)
    url = THEME_REPO_BASE_URL + encoded_filename
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"[ERROR] Failed to fetch theme content for {filename}: {e}")
        return None

def get_local_theme_metadata(file_path):
    """
    Reads the first few lines of a CSS file to extract metadata.
    Looks for /* VERSION: ... */, /* AUTHOR: ... */, /* NAME: ... */, /* DESCRIPTION: ... */
    Returns a dict with keys 'version', 'author', 'name', 'description'.
    """
    metadata = {'version': None, 'author': None, 'name': None, 'description': None}
    try:
        if not file_path.exists():
            return metadata
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first 10 lines to find metadata
            for _ in range(10):
                line = f.readline().strip()
                if not line: continue
                
                if 'VERSION:' in line:
                    parts = line.split('VERSION:')
                    if len(parts) > 1:
                        metadata['version'] = parts[1].split('*/')[0].strip()
                        
                if 'AUTHOR:' in line:
                    parts = line.split('AUTHOR:')
                    if len(parts) > 1:
                        metadata['author'] = parts[1].split('*/')[0].strip()

                if 'NAME:' in line:
                    parts = line.split('NAME:')
                    if len(parts) > 1:
                        metadata['name'] = parts[1].split('*/')[0].strip()

                if 'DESCRIPTION:' in line:
                    parts = line.split('DESCRIPTION:')
                    if len(parts) > 1:
                        metadata['description'] = parts[1].split('*/')[0].strip()
                        
    except Exception:
        pass
    return metadata

# --- Git Update Helpers ---
def git_check_update():
    """
    Checks for updates by fetching origin and comparing HEAD with origin/<current_branch>.
    Returns: (update_available: bool, message: str)
    """
    try:
        # 1. Fetch changes
        subprocess.check_call(['git', 'fetch'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Determine current branch
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('ascii').strip()
        if branch == "HEAD": # Detached HEAD state
            return False, "Update-Prüfung nicht möglich (Detached HEAD)"
            
        remote_ref = f"origin/{branch}"

        # 2. Get hash of HEAD
        local_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
        
        # 3. Get hash of upstream branch
        try:
            remote_hash = subprocess.check_output(['git', 'rev-parse', remote_ref]).decode('ascii').strip()
        except subprocess.CalledProcessError:
             return False, f"Remote-Branch '{remote_ref}' nicht gefunden."
        
        # Check for uncommitted changes
        is_dirty = False
        try:
            status = subprocess.check_output(['git', 'status', '--porcelain']).decode('ascii').strip()
            if status:
                is_dirty = True
        except Exception:
            pass

        if local_hash != remote_hash:
            # Check if we are behind
            # "git rev-list --count HEAD..origin/branch" returns number of commits we are behind
            behind_count = subprocess.check_output(['git', 'rev-list', '--count', f'HEAD..{remote_ref}']).decode('ascii').strip()
            if int(behind_count) > 0:
                msg = f"Update verfügbar ({behind_count} Commits hinter {remote_ref})"
                if is_dirty:
                    msg += " [Achtung: Lokale Änderungen vorhanden!]"
                return True, msg
            else:
                msg = "Lokale Version ist neuer oder divergiert."
                if is_dirty:
                    msg += " (Lokale Änderungen)"
                return False, msg
        
        if is_dirty:
             return False, "System ist aktuell (aber lokale Änderungen vorhanden)."

        return False, "System ist auf dem neuesten Stand."
        
    except Exception as e:
        return False, f"Fehler bei Update-Prüfung: {e}"

def git_perform_update():
    """
    Performs a git pull.
    Returns: (success: bool, message: str)
    """
    try:
        # git pull
        output = subprocess.check_output(['git', 'pull'], stderr=subprocess.STDOUT).decode('utf-8')
        return True, f"Update erfolgreich!\n{output}"
    except subprocess.CalledProcessError as e:
        return False, f"Update fehlgeschlagen:\n{e.output.decode('utf-8')}"
    except Exception as e:
        return False, f"Unerwarteter Fehler: {e}"

# --- Encryption Helpers ---
def load_key():
    """Loads the encryption key from file, or generates it if missing."""
    if not KEY_PATH.exists():
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as key_file:
            key_file.write(key)
        return key
    return open(KEY_PATH, "rb").read()

def encrypt_value(value):
    """Encrypts a string value."""
    if not value: return ""
    f = Fernet(load_key())
    return f.encrypt(value.encode()).decode()

def decrypt_value(value):
    """Decrypts a string value. Returns original value if decryption fails (e.g. was plaintext)."""
    if not value: return ""
    try:
        f = Fernet(load_key())
        return f.decrypt(value.encode()).decode()
    except (InvalidToken, Exception):
        # If decryption fails, assume it's plaintext (migration scenario)
        return value

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

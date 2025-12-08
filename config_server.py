import configparser
import threading
import os
import time
from pathlib import Path
from flask import Flask, render_template, request, flash, redirect, url_for
from wtforms import Form, StringField, IntegerField, BooleanField, PasswordField, TextAreaField, FloatField, validators

# Configuration Paths
APP_DIR = Path(__file__).parent
CONFIG_PATH = APP_DIR / "config.ini"
CSS_PATH = APP_DIR / "style.css"
RESTART_TRIGGER_PATH = APP_DIR / ".restart_trigger"

app = Flask(__name__)
app.secret_key = 'adarts-browser-secret-key'  # Needed for flash messages

class ConfigForm(Form):
    # Main Section
    browsers = IntegerField('Anzahl Browser (1 oder 2)', [validators.NumberRange(min=1, max=2)])
    refresh_interval_min = IntegerField('Auto-Refresh Intervall (Minuten, 0 = aus)')
    zoom_factor = FloatField('Zoom-Faktor (z.B. 1.0 = 100%, 1.2 = 120%)')
    screen = IntegerField('Bildschirm Index (0 = Hauptbildschirm)')
    
    # Boards Section
    board1_id = StringField('Board 1 ID (UUID)')
    board2_id = StringField('Board 2 ID (UUID)')
    
    # Style Section
    style_activate = BooleanField('Eigenes Styling (style.css) aktivieren')
    
    # Logos Section
    logos_enable = BooleanField('Logo anzeigen')
    logos_local = BooleanField('Lokales Logo verwenden')
    logos_logo = StringField('Logo URL oder Pfad')
    
    # Autologin Section
    autologin_enable = BooleanField('Auto-Login aktivieren')
    autologin_username = StringField('Benutzername (Email)')
    autologin_password = PasswordField('Passwort')
    autologin_versuche = IntegerField('Max. Login-Versuche')

class CSSForm(Form):
    css_content = TextAreaField('CSS Inhalt')

def read_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config

def delayed_restart_trigger():
    """Touches the restart trigger file after a short delay."""
    def run():
        time.sleep(1.0)  # Wait for response to be sent
        try:
            if not RESTART_TRIGGER_PATH.exists():
                RESTART_TRIGGER_PATH.touch()
            os.utime(RESTART_TRIGGER_PATH, None)
        except OSError:
            pass
    threading.Thread(target=run, daemon=True).start()

def write_config(config):
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
    
    delayed_restart_trigger()

def read_css():
    if not CSS_PATH.exists():
        return ""
    try:
        with open(CSS_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"/* Fehler beim Lesen der CSS-Datei: {e} */"

def write_css(content):
    try:
        with open(CSS_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    config = read_config()
    form = ConfigForm(request.form)

    if request.method == 'POST' and form.validate():
        # Update config object from form data
        if not config.has_section('main'): config.add_section('main')
        config.set('main', 'browsers', str(form.browsers.data))
        config.set('main', 'refresh_interval_min', str(form.refresh_interval_min.data))
        config.set('main', 'zoom_factor', str(form.zoom_factor.data))
        config.set('main', 'screen', str(form.screen.data))

        if not config.has_section('boards'): config.add_section('boards')
        config.set('boards', 'board1_id', form.board1_id.data)
        config.set('boards', 'board2_id', form.board2_id.data)

        if not config.has_section('style'): config.add_section('style')
        config.set('style', 'activate', str(form.style_activate.data).lower())

        if not config.has_section('logos'): config.add_section('logos')
        config.set('logos', 'enable', str(form.logos_enable.data).lower())
        config.set('logos', 'local', str(form.logos_local.data).lower())
        config.set('logos', 'logo', form.logos_logo.data)

        if not config.has_section('autologin'): config.add_section('autologin')
        config.set('autologin', 'enable', str(form.autologin_enable.data).lower())
        config.set('autologin', 'username', form.autologin_username.data)
        config.set('autologin', 'passwort', form.autologin_password.data)
        config.set('autologin', 'versuche', str(form.autologin_versuche.data))

        write_config(config)
        flash('Konfiguration gespeichert! Anwendung startet neu...', 'success')
        return redirect(url_for('index'))

    # Populate form from config (GET request)
    try:
        form.browsers.data = config.getint('main', 'browsers', fallback=1)
        form.refresh_interval_min.data = config.getint('main', 'refresh_interval_min', fallback=0)
        form.zoom_factor.data = config.getfloat('main', 'zoom_factor', fallback=1.0)
        form.screen.data = config.getint('main', 'screen', fallback=0)
        
        form.board1_id.data = config.get('boards', 'board1_id', fallback='')
        form.board2_id.data = config.get('boards', 'board2_id', fallback='')
        
        form.style_activate.data = config.getboolean('style', 'activate', fallback=False)
        
        form.logos_enable.data = config.getboolean('logos', 'enable', fallback=False)
        form.logos_local.data = config.getboolean('logos', 'local', fallback=False)
        form.logos_logo.data = config.get('logos', 'logo', fallback='')
        
        form.autologin_enable.data = config.getboolean('autologin', 'enable', fallback=False)
        form.autologin_username.data = config.get('autologin', 'username', fallback='')
        form.autologin_password.data = config.get('autologin', 'passwort', fallback='')
        form.autologin_versuche.data = config.getint('autologin', 'versuche', fallback=3)

    except Exception as e:
        flash(f'Fehler beim Laden der Konfiguration: {e}', 'danger')

    return render_template('config.html', form=form)

@app.route('/css', methods=['GET', 'POST'])
def edit_css():
    form = CSSForm(request.form)
    if request.method == 'POST':
        if write_css(form.css_content.data):
            flash('CSS gespeichert! Änderungen werden nach Neustart wirksam (oder evtl. sofort beim nächsten Seitenladen).', 'success')
            # Triggering a config change is often the easiest way to restart the app, 
            # but modifying CSS doesn't automatically touch config.ini.
            # However, the user might expect a restart.
            # Since the watcher watches config.ini, maybe we should touch it? 
            # Or just let the user know. 
            # Actually, `darts-browser.py` reads css on page load. So a simple refresh might be enough?
            # But the app doesn't refresh automatically on CSS change.
            # Let's just save it.
            return redirect(url_for('edit_css'))
        else:
            flash('Fehler beim Speichern der CSS-Datei.', 'danger')

    # GET request
    form.css_content.data = read_css()
    return render_template('edit_css.html', form=form)


@app.route('/restart', methods=['POST'])
def restart_app():
    delayed_restart_trigger()
    flash('Neustart ausgelöst! Die Anwendung startet in wenigen Sekunden neu.', 'info')
    return redirect(url_for('index'))


@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    try:
        # Create marker file
        marker_path = APP_DIR / ".clear_cache"
        marker_path.touch()
        
        delayed_restart_trigger()
        flash('Cache-Löschung angefordert! Anwendung startet neu...', 'info')
    except Exception as e:
        flash(f'Fehler beim Anfordern der Cache-Löschung: {e}', 'danger')
    
    return redirect(url_for('index'))


@app.route('/logs')
def view_logs():
    log_path = Path('/tmp/adarts-browser.log')
    logs = []
    if log_path.exists():
        try:
            # Read last 200 lines efficiently
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                # deque with maxlen is an efficient way to keep only the last N lines
                from collections import deque
                logs = list(deque(f, 200))
        except Exception as e:
            logs = [f"Fehler beim Lesen der Logdatei: {e}"]
    else:
        logs = ["Keine Logdatei gefunden (/tmp/adarts-browser.log).", 
                "Dies ist normal, wenn die Anwendung nicht über das Startskript gestartet wurde."]
    
    return render_template('logs.html', logs=logs)


def start_server(host='0.0.0.0', port=5000):
    """Starts the Flask server in a daemon thread with retry logic."""
    def run():
        retries = 10
        while retries > 0:
            try:
                # Disable Flask reloader to avoid main thread issues in PySide
                app.run(host=host, port=port, use_reloader=False)
                break # If run returns normally (it shouldn't usually), break loop
            except OSError as e:
                if "Address already in use" in str(e) or e.errno == 98:
                    print(f"[WARN] Port {port} is in use. Retrying in 1 second... ({retries} retries left)")
                    time.sleep(1)
                    retries -= 1
                else:
                    print(f"[ERROR] Failed to start config server: {e}")
                    break
            except Exception as e:
                print(f"[ERROR] Unexpected error starting config server: {e}")
                break
    
    server_thread = threading.Thread(target=run, daemon=True)
    server_thread.start()

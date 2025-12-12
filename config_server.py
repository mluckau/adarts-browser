import threading
import time
import zipfile
import io
import os
import shutil
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file, make_response
from wtforms import Form, StringField, IntegerField, BooleanField, PasswordField, TextAreaField, FloatField, validators, SelectField
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Import centralized configuration and utilities
from config import get_config
from utils import (
    APP_DIR, CSS_PATH, THEMES_DIR, LOG_PATH, CONFIG_PATH, THEME_REPO_BASE_URL,
    trigger_restart, trigger_reload, request_clear_cache, encrypt_value,
    git_check_update, git_perform_update,
    fetch_available_themes, fetch_theme_content, get_local_theme_metadata
)

app = Flask(__name__)
app.secret_key = 'adarts-browser-secret-key'  # Needed for flash messages
app.permanent_session_lifetime = timedelta(days=31) # Valid for 31 days if remember me is checked

@app.context_processor
def inject_device_info():
    config = get_config()
    return dict(global_device_name=config.device_name, global_version=config.version)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        config = get_config()
        if config.web_auth_enabled:
            if not session.get('logged_in'):
                return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        config = get_config()
        # Direct access to config properties for security check
        conf_user = config.web_username
        conf_hash = config.web_password_hash
        
        if username == conf_user and check_password_hash(conf_hash, password):
            session['logged_in'] = True
            if remember:
                session.permanent = True
            else:
                session.permanent = False
                
            flash('Erfolgreich eingeloggt.', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        else:
            flash('Ungültiger Benutzername oder Passwort.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Ausgeloggt.', 'info')
    return redirect(url_for('login'))

class ConfigForm(Form):
    # Main Section
    device_name = StringField('Gerätename (optional)')
    browsers = IntegerField('Anzahl Browser (1 oder 2)', [validators.NumberRange(min=1, max=2)])
    refresh_interval_min = IntegerField('Auto-Refresh Intervall (Minuten, 0 = aus)')
    zoom_factor = FloatField('Zoom-Faktor (z.B. 1.0 = 100%, 1.2 = 120%)')
    screen = IntegerField('Bildschirm Index (0 = Hauptbildschirm)')
    
    # Boards Section
    board1_id = StringField('Board 1 ID (UUID)')
    board2_id = StringField('Board 2 ID (UUID)')
    
    # Style Section
    style_activate = BooleanField('Eigenes Styling (style.css) aktivieren')
    view_mode = SelectField('Automatische Ansicht', choices=[
        ('none', 'Keine Änderung'),
        ('Segments mode', 'Segments Mode'),
        ('Coords mode', 'Coords Mode'),
        ('Live mode', 'Live Mode')
    ])
    
    # Logos Section
    logos_enable = BooleanField('Logo anzeigen')
    logos_local = BooleanField('Lokales Logo verwenden')
    logos_logo = StringField('Logo URL oder Pfad')
    
    # Autologin Section
    autologin_enable = BooleanField('Auto-Login aktivieren')
    autologin_username = StringField('Benutzername (Email)')
    autologin_password = PasswordField('Passwort')
    autologin_attempts = IntegerField('Max. Login-Versuche')

    # Security Section
    security_enable = BooleanField('Passwortschutz für Konfiguration aktivieren')
    security_username = StringField('Benutzername (Standard: admin)')
    security_new_password = PasswordField('Neues Passwort setzen (leer lassen zum Beibehalten)')
    
    # Advanced / QR
    show_qr = BooleanField('QR-Code beim Start anzeigen')
    qr_duration = IntegerField('Anzeigedauer des QR-Codes (Sekunden)')

class CSSForm(Form):
    css_content = TextAreaField('CSS Inhalt')

def strip_css_metadata(content):
    """Removes metadata comments (VERSION, AUTHOR, NAME, DESCRIPTION) from CSS content."""
    if not content: return ""
    lines = content.splitlines()
    filtered = []
    for line in lines:
        check = line.strip()
        if (check.startswith('/* VERSION:') or
            check.startswith('/* AUTHOR:') or
            check.startswith('/* NAME:') or
            check.startswith('/* DESCRIPTION:')):
            continue
        filtered.append(line)
    return "\n".join(filtered)

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

def _sanitize_theme_name(name):
    return "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()

# --- Theme Helper Functions ---
def list_themes():
    if not THEMES_DIR.exists():
        return []
    return sorted([f.stem for f in THEMES_DIR.glob('*.css')])

def save_theme(name, content):
    if not THEMES_DIR.exists():
        THEMES_DIR.mkdir(exist_ok=True)
    
    safe_name = _sanitize_theme_name(name)
    if not safe_name:
        return False
    try:
        with open(THEMES_DIR / f"{safe_name}.css", 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def load_theme(name):
    try:
        with open(THEMES_DIR / f"{name}.css", 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return None

def delete_theme(name):
    try:
        (THEMES_DIR / f"{name}.css").unlink()
        return True
    except Exception:
        return False

def rename_theme(old_name, new_name):
    if not THEMES_DIR.exists():
        return False
    
    safe_new_name = _sanitize_theme_name(new_name)
    if not safe_new_name:
        return False
        
    old_path = THEMES_DIR / f"{old_name}.css"
    new_path = THEMES_DIR / f"{safe_new_name}.css"
    
    if not old_path.exists():
        return False
        
    if new_path.exists():
        return False # Target already exists
        
    try:
        old_path.rename(new_path)
        return True
    except Exception:
        return False

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    config = get_config()
    form = ConfigForm(request.form)

    if request.method == 'POST' and form.validate():
        # Update config object from form data using the centralized AppConfig methods
        config.set('main', 'device_name', form.device_name.data)
        config.set('main', 'browsers', form.browsers.data)
        config.set('main', 'refresh_interval_min', form.refresh_interval_min.data)
        config.set('main', 'zoom_factor', form.zoom_factor.data)
        config.set('main', 'screen', form.screen.data)

        config.set('boards', 'board1_id', form.board1_id.data)
        config.set('boards', 'board2_id', form.board2_id.data)

        if not config.has_section('style'): config.add_section('style')
        config.set('style', 'activate', str(form.style_activate.data).lower())
        config.set('style', 'view_mode', form.view_mode.data)
        
        # Cleanup old setting to prevent conflicts
        if config.has_section('style'):
            config.remove_option('style', 'auto_coords_mode')
            # Also remove from [boards] if it was ever there (mistake in previous version)
            if config.has_section('boards'):
                config.remove_option('boards', 'auto_coords_mode')

        config.set('logos', 'enable', str(form.logos_enable.data).lower())
        config.set('logos', 'local', str(form.logos_local.data).lower())
        config.set('logos', 'logo', form.logos_logo.data)

        config.set('autologin', 'enable', str(form.autologin_enable.data).lower())
        config.set('autologin', 'username', form.autologin_username.data)
        
        # Only update password if a new one is provided
        new_autologin_pw = form.autologin_password.data
        if new_autologin_pw:
            encrypted_pw = encrypt_value(new_autologin_pw)
            config.set('autologin', 'password', encrypted_pw)
            
        config.set('autologin', 'attempts', form.autologin_attempts.data)

        # Security Section
        config.set('security', 'enable_auth', str(form.security_enable.data).lower())
        config.set('security', 'username', form.security_username.data)
        
        # Only update hash if a new password is provided
        new_pass = form.security_new_password.data
        if new_pass:
            hashed_pw = generate_password_hash(new_pass)
            config.set('security', 'password_hash', hashed_pw)
            
        # Advanced / QR
        config.set('main', 'show_qr', str(form.show_qr.data).lower())
        config.set('main', 'qr_duration', form.qr_duration.data)

        config.save()
        trigger_restart()
        flash('Konfiguration gespeichert! Anwendung startet neu...', 'success')
        return redirect(url_for('index'))

    # Populate form from config (GET request)
    try:
        # Use fallback values that match AppConfig properties defaults
        form.device_name.data = config.get('main', 'device_name', fallback='')
        form.browsers.data = config.getint('main', 'browsers', fallback=1)
        form.refresh_interval_min.data = config.getint('main', 'refresh_interval_min', fallback=0)
        form.zoom_factor.data = config.getfloat('main', 'zoom_factor', fallback=1.0)
        form.screen.data = config.getint('main', 'screen', fallback=0)
        
        # QR Defaults
        form.show_qr.data = config.getboolean('main', 'show_qr', fallback=True)
        form.qr_duration.data = config.getint('main', 'qr_duration', fallback=15)
        
        form.board1_id.data = config.get('boards', 'board1_id', fallback='')
        form.board2_id.data = config.get('boards', 'board2_id', fallback='')
        
        form.style_activate.data = config.getboolean('style', 'activate', fallback=False)
        form.view_mode.data = config.view_mode # Use property to handle migration logic
        
        form.logos_enable.data = config.getboolean('logos', 'enable', fallback=False)
        form.logos_local.data = config.getboolean('logos', 'local', fallback=False)
        form.logos_logo.data = config.get('logos', 'logo', fallback='')
        
        form.autologin_enable.data = config.getboolean('autologin', 'enable', fallback=False)
        form.autologin_username.data = config.get('autologin', 'username', fallback='')
        # Do not populate password field for security and because it might be encrypted
        form.autologin_password.data = "" 
        # Retrieve attempts from config.py using the new name
        form.autologin_attempts.data = config.getint('autologin', 'attempts', fallback=3)

        form.security_enable.data = config.getboolean('security', 'enable_auth', fallback=False)
        form.security_username.data = config.get('security', 'username', fallback='admin')

    except Exception as e:
        flash(f'Fehler beim Laden der Konfiguration: {e}', 'danger')

    device_info = {
        'name': config.device_name,
        'id': config.device_id
    }

    return render_template('config.html', form=form, device_info=device_info)

@app.route('/css', methods=['GET', 'POST'])
@login_required
def edit_css():
    form = CSSForm(request.form)
    
    if request.method == 'POST':
        action = request.form.get('action', 'save')
        
        if action == 'save':
            if write_css(form.css_content.data):
                flash('CSS gespeichert! Änderungen werden sofort live auf dem Bildschirm aktualisiert.', 'success')
            else:
                flash('Fehler beim Speichern der CSS-Datei.', 'danger')
                
        elif action == 'save_theme':
            theme_name = request.form.get('theme_name')
            if theme_name and save_theme(theme_name, form.css_content.data):
                flash(f'Theme "{theme_name}" gespeichert.', 'success')
            else:
                flash('Fehler beim Speichern des Themes (ungültiger Name?).', 'danger')
                
        elif action == 'load_theme':
            theme_name = request.form.get('selected_theme')
            content = load_theme(theme_name)
            if content is not None:
                # Strip metadata for editor view
                clean_content = strip_css_metadata(content)
                form.css_content.data = clean_content
                # Save the CLEAN content to style.css (active style)
                write_css(clean_content)
                flash(f'Theme "{theme_name}" geladen und angewendet.', 'success')
            else:
                flash('Fehler beim Laden des Themes.', 'danger')
                
        elif action == 'delete_theme':
            theme_name = request.form.get('selected_theme')
            if delete_theme(theme_name):
                flash(f'Theme "{theme_name}" gelöscht.', 'info')
            else:
                flash('Fehler beim Löschen des Themes.', 'danger')

        elif action == 'rename_theme':
            old_name = request.form.get('selected_theme')
            new_name = request.form.get('new_theme_name')
            if rename_theme(old_name, new_name):
                flash(f'Theme umbenannt in "{new_name}".', 'success')
            else:
                flash('Fehler beim Umbenennen (Name ungültig oder existiert bereits?).', 'danger')

        elif action == 'install_preset':
            preset_name = request.form.get('preset_name')
            preset_file = request.form.get('preset_file')
            preset_version = request.form.get('preset_version')
            preset_author = request.form.get('preset_author')
            
            if preset_name and preset_file:
                content = fetch_theme_content(preset_file)
                if content:
                    # Strip existing metadata to avoid duplication
                    content = strip_css_metadata(content)

                    # Prepend metadata
                    header = []
                    if preset_version:
                        header.append(f"/* VERSION: {preset_version} */")
                    if preset_author:
                        header.append(f"/* AUTHOR: {preset_author} */")
                    
                    if header:
                        content = "\n".join(header) + "\n" + content
                        
                    if save_theme(preset_name, content):
                        flash(f'Theme "{preset_name}" (v{preset_version}) erfolgreich installiert.', 'success')
                    else:
                        flash('Fehler beim Speichern des Themes.', 'danger')
                else:
                    flash('Fehler beim Herunterladen des Themes (Verbindung oder Datei?).', 'danger')
            else:
                flash('Ungültige Preset-Daten.', 'danger')

        return redirect(url_for('edit_css'))

    # GET request
    raw_content = read_css()
    form.css_content.data = strip_css_metadata(raw_content)
    
    # Enrich local themes
    theme_names = list_themes()
    themes = []
    for name in theme_names:
        path = THEMES_DIR / f"{name}.css"
        meta = get_local_theme_metadata(path)
        themes.append({
            'name': name,
            'version': meta.get('version'),
            'author': meta.get('author')
        })

    online_themes = fetch_available_themes()
    
    # Process online themes to check installation status
    for theme in online_themes:
        # Determine local filename
        safe_name = _sanitize_theme_name(theme.get('name', ''))
        local_path = THEMES_DIR / f"{safe_name}.css"
        
        theme['is_installed'] = False
        theme['update_available'] = False
        theme['local_version'] = None
        
        if local_path.exists():
            theme['is_installed'] = True
            meta = get_local_theme_metadata(local_path)
            local_ver = meta.get('version')
            theme['local_version'] = local_ver
            
            # Simple string comparison for versions (works for 1.0 vs 1.1, but ideally use semver)
            online_ver = theme.get('version')
            if online_ver and local_ver and online_ver > local_ver:
                theme['update_available'] = True
            # Also if installed but no local version found (legacy installation), treat as update available if online has version
            if online_ver and not local_ver:
                 theme['update_available'] = True

    response = make_response(render_template('edit_css.html', form=form, themes=themes, presets=online_themes, repo_url=THEME_REPO_BASE_URL))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/restart', methods=['POST'])
@login_required
def restart_app():
    trigger_restart()
    flash('Neustart ausgelöst! Die Anwendung startet in wenigen Sekunden neu.', 'info')
    return redirect(url_for('index'))

@app.route('/reload_pages', methods=['POST'])
@login_required
def reload_pages():
    trigger_reload()
    flash('Seiten-Neuladen ausgelöst! Die Browserseiten werden aktualisiert.', 'info')
    return redirect(url_for('index'))


@app.route('/clear_cache', methods=['POST'])
@login_required
def clear_cache():
    if request_clear_cache():
        flash('Cache-Löschung angefordert! Anwendung startet neu...', 'info')
    else:
        flash('Fehler beim Anfordern der Cache-Löschung.', 'danger')
    
    return redirect(url_for('index'))


@app.route('/logs')
@login_required
def view_logs():
    logs = []
    if LOG_PATH.exists():
        try:
            # Read last 200 lines efficiently
            with open(LOG_PATH, 'r', encoding='utf-8', errors='replace') as f:
                # deque with maxlen is an efficient way to keep only the last N lines
                from collections import deque
                logs = list(deque(f, 200))
        except Exception as e:
            logs = [f"Fehler beim Lesen der Logdatei: {e}"]
    else:
        logs = ["Keine Logdatei gefunden (/tmp/adarts-browser.log).", 
                "Dies ist normal, wenn die Anwendung nicht über das Startskript gestartet wurde."]
    
    return render_template('logs.html', logs=logs)


@app.route('/check_update', methods=['POST'])
@login_required
def check_update():
    available, msg = git_check_update()
    if available:
        flash(f"{msg}", 'info')
        # Store update availability in session to show update button
        session['update_available'] = True
    else:
        flash(f"{msg}", 'success')
        session.pop('update_available', None)
    
    return redirect(url_for('index'))

@app.route('/perform_update', methods=['POST'])
@login_required
def perform_update():
    success, msg = git_perform_update()
    if success:
        flash("Update erfolgreich installiert! Anwendung wird neu gestartet...", 'success')
        session.pop('update_available', None)
        # Trigger restart slightly delayed to allow flash message to be rendered? 
        # Actually restart will kill server, so maybe just trigger it and hope browser reconnects.
        trigger_restart()
    else:
        flash(f"Fehler beim Update: {msg}", 'danger')
        
    return redirect(url_for('index'))

@app.route('/backup')
@login_required
def create_backup():
    try:
        # Create in-memory zip
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add config.ini
            if CONFIG_PATH.exists():
                zf.write(CONFIG_PATH, arcname='config.ini')
            
            # Add style.css
            if CSS_PATH.exists():
                zf.write(CSS_PATH, arcname='style.css')
            
            # Add themes folder
            if THEMES_DIR.exists():
                for root, dirs, files in os.walk(THEMES_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Archive name relative to THEMES_DIR parent, so it includes 'themes/'
                        arcname = os.path.relpath(file_path, APP_DIR)
                        zf.write(file_path, arcname=arcname)
        
        memory_file.seek(0)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'adarts-backup-{timestamp}.zip'
        )
    except Exception as e:
        flash(f'Fehler beim Erstellen des Backups: {e}', 'danger')
        return redirect(url_for('index'))

@app.route('/restore', methods=['POST'])
@login_required
def restore_backup():
    if 'backup_file' not in request.files:
        flash('Keine Datei ausgewählt.', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['backup_file']
    if file.filename == '':
        flash('Keine Datei ausgewählt.', 'danger')
        return redirect(url_for('index'))

    if file and file.filename.endswith('.zip'):
        try:
            # Verify zip content first
            with zipfile.ZipFile(file) as zf:
                # Basic validation: check for expected files
                file_names = zf.namelist()
                if not any(f in file_names for f in ['config.ini', 'style.css']) and not any(f.startswith('themes/') for f in file_names):
                    flash('Ungültiges Backup-Archiv: Weder config.ini noch style.css oder Themes gefunden.', 'warning')
                    return redirect(url_for('index'))
                
                # Extract
                # We extract to APP_DIR. 
                # Warning: zipfile.extractall can be dangerous if zip contains absolute paths or '..'.
                # But we trust the user here (authenticated admin).
                for member in zf.infolist():
                    # Security: skip absolute paths or ..
                    if member.filename.startswith('/') or '..' in member.filename:
                        continue
                        
                    # Target path
                    target_path = APP_DIR / member.filename
                    
                    # Create directory if needed
                    if member.is_dir():
                        target_path.mkdir(parents=True, exist_ok=True)
                    else:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(target_path, 'wb') as f:
                            f.write(zf.read(member))
            
            flash('Backup erfolgreich wiederhergestellt! Anwendung startet neu...', 'success')
            trigger_restart()
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Fehler beim Wiederherstellen: {e}', 'danger')
            return redirect(url_for('index'))
    else:
        flash('Nur .zip Dateien sind erlaubt.', 'danger')
        return redirect(url_for('index'))


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
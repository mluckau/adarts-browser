import sys
import os
import shutil
import threading
import time
import subprocess
import base64
import json
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import QUrl, QFile, Qt, QTimer, QFileSystemWatcher
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEnginePage,
    QWebEngineScript,
    QWebEngineSettings,
)
from config import AppConfig
from http_server import ServeDirectoryWithHTTP
from config_server import start_server
from utils import (
    APP_DIR, SCRIPTS_DIR, CONFIG_PATH, CSS_PATH,
    RESTART_TRIGGER_PATH, RELOAD_TRIGGER_PATH, CLEAR_CACHE_MARKER_PATH
)

# --- Global Config ---
config = AppConfig(CONFIG_PATH)

# --- Script Templates ---
try:
    with open(SCRIPTS_DIR / "login.js", "r") as f:
        LOGIN_SCRIPT_TPL = f.read()
    with open(SCRIPTS_DIR / "logo.js", "r") as f:
        LOGO_SCRIPT_TPL = f.read()
    with open(SCRIPTS_DIR / "inject_css.js", "r") as f:
        CSS_INJECT_TPL = f.read()
    with open(APP_DIR / "templates" / "offline_page.html", "r", encoding="utf-8") as f:
        OFFLINE_PAGE_TPL = f.read()
    with open(SCRIPTS_DIR / "offline_check.js", "r") as f:
        OFFLINE_CHECK_SCRIPT_TPL = f.read()
except FileNotFoundError as e:
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "Script Error",
                         f"A script file was not found.\n{e}")
    sys.exit(1)


def run_script(view, script_code, name=""):
    """Helper to create and run a QWebEngineScript."""
    script = QWebEngineScript()
    script.setSourceCode(script_code)
    script.setInjectionPoint(QWebEngineScript.DocumentReady)
    script.setRunsOnSubFrames(True)
    script.setWorldId(QWebEngineScript.ApplicationWorld)
    view.page.scripts().insert(script)


class BrowserView(QWebEngineView):
    """A self-contained browser widget for displaying a single Autodarts board."""

    def __init__(self, browser_id, target_url, parent=None):
        super().__init__(parent)
        self.browser_id = browser_id
        self.target_url = target_url
        self.login_attempts = 0

        # Create profile and page without parents to manage their lifecycle manually
        self.profile = QWebEngineProfile(f"browser-{browser_id}")

        # Ensure cache directory is relative to the app's directory
        cache_dir = config.cache_dir.lstrip('/\\')
        self.profile.setPersistentStoragePath(
            str(APP_DIR / cache_dir / f"browser{self.browser_id}"))

        self.page = QWebEnginePage(self.profile)
        self.page.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        self.setPage(self.page)

        self.loadFinished.connect(self._on_load_finished)

    def load_target_url(self):
        if self.target_url:
            self.setUrl(QUrl(self.target_url))

    def _on_load_finished(self, ok):
        current_url = self.url().toString().split("#")[0]
        is_target_page = current_url == self.target_url

        if not ok:
            print(
                f"[Browser {self.browser_id}] Page failed to load: {current_url}")
            return
        
        # Apply Zoom Factor
        self.setZoomFactor(config.zoom_factor)

        if is_target_page:
            print(
                f"[Browser {self.browser_id}] Successfully loaded target URL.")
            self.login_attempts = 0  # Reset login attempts on success

            if config.use_custom_style:
                self._inject_css()
            if config.logos_enabled:
                self._insert_logo()

            # Always try to inject autologin script, in case login form is on the target page
            if config.autologin_enabled:
                 # Check max attempts even for target page to be safe, though usually we want to retry if we landed here but are logged out
                 if self.login_attempts < config.autologin_max_attempts:
                    self.login_attempts += 1
                    self._inject_autologin()

        else:
            print(
                f"[Browser {self.browser_id}] Redirected to {current_url}. Attempting login... (Attempt {self.login_attempts + 1}/{config.autologin_max_attempts})")
            if config.autologin_enabled:
                if self.login_attempts < config.autologin_max_attempts:
                    self.login_attempts += 1
                    self._inject_autologin()
                else:
                    print(f"[Browser {self.browser_id}] Max login attempts reached. Stopping autologin.")
        
        # Inject offline check script
        self._inject_offline_check()

    def _inject_autologin(self):
        print(f"[Browser {self.browser_id}] Injecting autologin script... (Attempt {self.login_attempts}/{config.autologin_max_attempts})")
        
        # No need to check for empty here, if config is empty, the JS will simply try to set empty values.
        # This will be handled by the login page, which will probably reject empty credentials.

        script_code = LOGIN_SCRIPT_TPL.replace(
            '{username}', config.autologin_username
        ).replace(
            '{password}', config.autologin_password
        )
        run_script(self, script_code, name="autologin")
        self.page.runJavaScript(script_code)

    def _try_login(self):
        pass

    def _inject_css(self):
        # Always try to read CSS, even if it doesn't exist (empty string)
        css_content = ""
        if CSS_PATH.exists():
            try:
                with open(CSS_PATH, "r", encoding="utf-8") as f:
                    css_content = f.read()
            except Exception as e:
                print(f"[Browser {self.browser_id}] Error reading style.css: {e}")
                return

        # Use Base64 encoding to safely pass CSS to JS
        try:
            css_b64 = base64.b64encode(css_content.encode('utf-8')).decode('ascii').replace('\n', '').replace('\r', '').strip()
            
            script_code = CSS_INJECT_TPL.replace(
                "{css_b64}", css_b64
            )
            # We run this directly to update immediately
            self.page.runJavaScript(script_code)
            print(f"[Browser {self.browser_id}] Injected/Updated custom CSS.")
        except Exception as e:
            print(f"[Browser {self.browser_id}] Error injecting CSS: {e}")

    def _insert_logo(self):
        if config.logos_local:
            if self.local_http_port:
                logo_url = f"http://localhost:{self.local_http_port}/{config.logo_source}"
            else:
                print("[ERROR] Local HTTP server not started, cannot serve local logo.")
                return
        else:
            logo_url = config.logo_source

        script_code = LOGO_SCRIPT_TPL.replace('{logo_url}', logo_url)
        run_script(self, script_code, name="logo")
        self.page.runJavaScript(script_code)
        print(f"[Browser {self.browser_id}] Injected logo.")

    def _inject_offline_check(self):
        print(f"[Browser {self.browser_id}] Injecting offline check script...")
        
        try:
            # Use Base64 encoding for HTML content as well
            html_b64 = base64.b64encode(OFFLINE_PAGE_TPL.encode('utf-8')).decode('ascii').replace('\n', '').replace('\r', '').strip()
            
            script_code = OFFLINE_CHECK_SCRIPT_TPL.replace(
                '{offline_html_b64}', html_b64
            )
            run_script(self, script_code, name="offlineCheck")
        except Exception as e:
            print(f"[Browser {self.browser_id}] Error injecting offline check: {e}")


class AutodartsBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self._cleanup_started = False
        self._is_restarting = False
        self.browsers = []
        self.http_server = None
        self.local_http_port = None # Initialize local HTTP server port

        self.start_http_server()
        self.init_ui()
        self.load_pages()
        self.init_refresh_timer()
        self.init_config_watcher()

    def init_ui(self):
        self.setWindowTitle("Autodarts Webbrowser")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setStyleSheet("background-color: black;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create Browser 1
        url1 = config.get_board_url(1)
        if not url1:
            print("[INFO] No Board URL configured. Loading setup_needed.html.")
            url1 = f"file://{APP_DIR / 'templates' / 'setup_needed.html'}"

        browser1 = BrowserView(1, url1, self)
        self.browsers.append(browser1)
        self.layout.addWidget(browser1)

        # Create Browser 2 if enabled
        if config.browser_count >= 2:
            url2 = config.get_board_url(2)
            browser2 = BrowserView(2, url2, self)
            self.browsers.append(browser2)
            self.layout.addWidget(browser2)

    def start_http_server(self):
        if config.logos_enabled and config.logos_local: # Only start if local logos are enabled
            self.http_server, _, self.local_http_port = ServeDirectoryWithHTTP(
                directory=str(APP_DIR))
            print(f"[INFO] Local HTTP server started on port: {self.local_http_port}")
        else:
            self.local_http_port = 3344 # Fallback to default if local server is not started (e.g. for logos_local=False case)

    def load_pages(self):
        for browser in self.browsers:
            browser.load_target_url()

    def refresh_pages(self):
        print("[INFO] Auto-refreshing all pages...")
        for browser in self.browsers:
            browser.reload()
            
    def update_css(self):
        print("[INFO] Updating CSS in all browsers...")
        for browser in self.browsers:
            browser._inject_css()

    def init_refresh_timer(self):
        interval_min = config.refresh_interval_min
        if interval_min > 0:
            self.refresh_timer = QTimer(self)
            self.refresh_timer.timeout.connect(self.refresh_pages)
            interval_ms = interval_min * 60 * 1000
            self.refresh_timer.start(interval_ms)
            print(
                f"[INFO] Auto-refresh enabled. Interval: {interval_min} minutes.")

    def init_config_watcher(self):
        self.watcher = QFileSystemWatcher()
        
        # Watch config file
        self.watcher.addPath(str(CONFIG_PATH))
        
        # Watch style file
        if not CSS_PATH.exists():
            CSS_PATH.touch()
        self.watcher.addPath(str(CSS_PATH))
        
        # Watch restart trigger file
        if not RESTART_TRIGGER_PATH.exists():
            RESTART_TRIGGER_PATH.touch()
        self.watcher.addPath(str(RESTART_TRIGGER_PATH))
        
        # Watch reload trigger file
        if not RELOAD_TRIGGER_PATH.exists():
            RELOAD_TRIGGER_PATH.touch()
        self.watcher.addPath(str(RELOAD_TRIGGER_PATH))
        
        # Connect signal to a single handler
        self.watcher.fileChanged.connect(self._on_file_changed)


    def _on_file_changed(self, path):
        changed_path = str(Path(path).absolute())
        print(f"[DEBUG] File changed: {changed_path}")
        
        if str(CONFIG_PATH.absolute()) == changed_path:
            print("[INFO] config.ini changed. Scheduling restart.")
            self._trigger_restart()
            
        elif str(CSS_PATH.absolute()) == changed_path:
            print("[INFO] style.css changed. Updating styles.")
            self.update_css()
            
        elif str(RESTART_TRIGGER_PATH.absolute()) == changed_path:
            print("[INFO] Restart trigger file touched. Scheduling restart.")
            self._trigger_restart()
            
        elif str(RELOAD_TRIGGER_PATH.absolute()) == changed_path:
            print("[INFO] Reload trigger detected. Reloading all browser pages.")
            self.refresh_pages()

    def _trigger_restart(self):
        self._is_restarting = True
        # Stop watching to prevent multiple triggers
        if self.watcher:
            self.watcher.removePaths(self.watcher.files())
        QApplication.instance().quit()

    def cleanup(self):
        if self._cleanup_started:
            return
        self._cleanup_started = True

        print("[INFO] Cleaning up resources...")
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()

        if self.http_server:
            print("[INFO] Shutting down HTTP server...")
            self.http_server.shutdown()
            # The server thread is a daemon, but shutdown allows a clean exit.

        for browser in self.browsers:
            browser.close()
            browser.setPage(None)

            # Manually schedule deletion in the correct order
            browser.page.deleteLater()
            browser.profile.deleteLater()
            browser.deleteLater()

        print("[INFO] Cleanup complete. Quitting application.")
        # Use a timer to allow deleteLater events to be processed
        QTimer.singleShot(200, QApplication.instance().quit)


def perform_cache_cleanup():
    if CLEAR_CACHE_MARKER_PATH.exists():
        print("[INFO] Clear cache marker found. Deleting cache...")
        cache_dir_rel = config.cache_dir.lstrip('/\\')
        cache_dir = APP_DIR / cache_dir_rel
        try:
            if cache_dir.exists():
                # Safeguard: Ensure we are not deleting critical directories
                resolved_cache_dir = cache_dir.resolve()
                resolved_app_dir = APP_DIR.resolve()

                # Prevent deleting the app's root directory or its parent
                if resolved_cache_dir == resolved_app_dir or resolved_cache_dir == resolved_app_dir.parent:
                    print(
                        f"[ERROR] Attempt to delete application root or parent directory as cache: {cache_dir}. Aborting cache clear.")
                    return
                # Also check if cache_dir is a critical system path (e.g. root)
                if str(resolved_cache_dir) == '/':
                    print(
                        f"[ERROR] Attempt to delete root directory as cache. Aborting cache clear.")
                    return

                shutil.rmtree(cache_dir)
                print(f"[INFO] Cache directory {cache_dir} deleted.")
            CLEAR_CACHE_MARKER_PATH.unlink()
            print("[INFO] Marker file removed.")
        except Exception as e:
            print(f"[ERROR] Failed to clear cache: {e}")


def main():
    try:
        # Check for cache clear request
        perform_cache_cleanup()

        # Start the configuration server
        print("Starting configuration server on http://0.0.0.0:5000")
        start_server()

        app = QApplication(sys.argv)

        # --- Screen Selection ---
        screens = app.screens()
        target_screen_index = config.screen
        if target_screen_index < 0 or target_screen_index >= len(screens):
            print(f"[WARN] Screen index {target_screen_index} is invalid. "
                  f"Defaulting to primary screen 0.")
            target_screen_index = 0

        target_screen = screens[target_screen_index]
        print(f"[INFO] Using screen {target_screen_index}: {target_screen.name()}")

        main_window = AutodartsBrowser()
        main_window.setScreen(target_screen)
        main_window.showFullScreen()

        app.aboutToQuit.connect(main_window.cleanup)

        exit_code = app.exec()

        if main_window._is_restarting:
            print("[INFO] Restarting application...")
            # Give some time for resources (like port 5000) to be released
            time.sleep(2)
            # Clean restart using subprocess to release all file descriptors (sockets)
            subprocess.Popen([sys.executable] + sys.argv)
            sys.exit(0)
        else:
            print("[INFO] Application has exited.")
            sys.exit(exit_code)
            
    except Exception as e:
        import traceback
        with open("crash.log", "w") as f:
            f.write(traceback.format_exc())
        print(f"[CRITICAL] Application crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

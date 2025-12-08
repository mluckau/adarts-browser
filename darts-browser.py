import sys
import os
import shutil
import threading
import time
import subprocess
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

# --- Constants & Global Config ---
APP_DIR = Path(__file__).parent
SCRIPTS_DIR = APP_DIR / "scripts"
CONFIG_PATH = APP_DIR / "config.ini"
RESTART_TRIGGER_PATH = APP_DIR / ".restart_trigger" # Restart trigger path
RELOAD_TRIGGER_PATH = APP_DIR / ".reload_trigger" # Reload trigger path
config = AppConfig(CONFIG_PATH)

# --- Script Templates ---
try:
    with open(SCRIPTS_DIR / "login.js", "r") as f:
        LOGIN_SCRIPT_TPL = f.read()
    with open(SCRIPTS_DIR / "logo.js", "r") as f:
        LOGO_SCRIPT_TPL = f.read()
    with open(SCRIPTS_DIR / "inject_css.js", "r") as f:
        CSS_INJECT_TPL = f.read()
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
                self._inject_autologin()

        else:
            print(
                f"[Browser {self.browser_id}] Redirected to {current_url}. Attempting login...")
            if config.autologin_enabled:
                self._inject_autologin()

    def _inject_autologin(self):
        print(f"[Browser {self.browser_id}] Injecting autologin script...")
        script_code = LOGIN_SCRIPT_TPL.replace(
            '{username}', config.autologin_username
        ).replace(
            '{password}', config.autologin_password
        )
        run_script(self, script_code, name="autologin")

    def _try_login(self):
        # Deprecated: logic moved to _inject_autologin and handled in _on_load_finished directly
        pass

    def _inject_css(self):
        css_path = QFile(APP_DIR / "style.css")
        if not css_path.open(QFile.ReadOnly | QFile.Text):
            print(f"[Browser {self.browser_id}] Could not open style.css")
            return
        css_content = css_path.readAll().data().decode("utf-8").replace("`", "\\`")
        script_code = CSS_INJECT_TPL.replace(
            "{name}", "injectedCSS"
        ).replace(
            "{css}", css_content
        )
        run_script(self, script_code, name="injectedCSS")
        self.page.runJavaScript(script_code)
        print(f"[Browser {self.browser_id}] Injected custom CSS.")

    def _insert_logo(self):
        if config.logos_local:
            logo_url = f"http://localhost:3344/{config.logo_source}"
        else:
            logo_url = config.logo_source

        script_code = LOGO_SCRIPT_TPL.replace('{logo_url}', logo_url)
        run_script(self, script_code, name="logo")
        self.page.runJavaScript(script_code)
        print(f"[Browser {self.browser_id}] Injected logo.")


class AutodartsBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self._cleanup_started = False
        self._is_restarting = False
        self.browsers = []
        self.http_server = None

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
        if config.use_custom_style and config.logos_enabled and config.logos_local:
            self.http_server, _ = ServeDirectoryWithHTTP(
                directory=str(APP_DIR))

    def load_pages(self):
        for browser in self.browsers:
            browser.load_target_url()

    def refresh_pages(self):
        print("[INFO] Auto-refreshing all pages...")
        for browser in self.browsers:
            browser.reload()

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


def check_and_clear_cache():
    marker_path = APP_DIR / ".clear_cache"
    if marker_path.exists():
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
            marker_path.unlink()
            print("[INFO] Marker file removed.")
        except Exception as e:
            print(f"[ERROR] Failed to clear cache: {e}")


def main():
    try:
        # Check for cache clear request
        check_and_clear_cache()

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


import sys
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import QUrl, QFile, Qt, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEnginePage,
    QWebEngineScript,
    QWebEngineSettings,
)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import AppConfig

# --- Constants & Global Config ---
try:
    APP_DIR = Path(__file__).parent
    SCRIPTS_DIR = APP_DIR / "scripts"
    CONFIG_PATH = APP_DIR / "config.ini"
    config = AppConfig(CONFIG_PATH)
except FileNotFoundError as e:
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "Configuration Error",
                         f"Configuration file not found.\n{e}")
    sys.exit(1)

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

# --- HTTP Server ---
if config.use_custom_style and config.logos_enabled and config.logos_local:
    from http_server import ServeDirectoryWithHTTP
    ServeDirectoryWithHTTP(directory=str(APP_DIR))


def run_script(view, script_code, name=""):
    """Helper to create and run a QWebEngineScript."""
    script = QWebEngineScript()
    view.page.runJavaScript(script_code, QWebEngineScript.ApplicationWorld)
    if name:
        script.setName(name)
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
        self.page.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
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

        if is_target_page:
            print(
                f"[Browser {self.browser_id}] Successfully loaded target URL.")
            if config.use_custom_style:
                self._inject_css()
            if config.logos_enabled:
                self._insert_logo()
        else:
            print(
                f"[Browser {self.browser_id}] Redirected to {current_url}. Attempting login...")
            self._try_login()

    def _try_login(self):
        if not config.autologin_enabled:
            print(f"[Browser {self.browser_id}] Autologin disabled.")
            return

        if self.login_attempts < config.autologin_max_attempts:
            self.login_attempts += 1
            print(
                f"[Browser {self.browser_id}] Attempting login {self.login_attempts}/{config.autologin_max_attempts}")
            script_code = LOGIN_SCRIPT_TPL.replace(
                '{username}', config.autologin_username
            ).replace(
                '{password}', config.autologin_password
            )
            run_script(self, script_code)
        else:
            print(f"[Browser {self.browser_id}] Max login attempts reached.")

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
        print(f"[Browser {self.browser_id}] Injected custom CSS.")

    def _insert_logo(self):
        if config.logos_local:
            logo_url = f"http://localhost:3344/{config.logo_source}"
        else:
            logo_url = config.logo_source

        script_code = LOGO_SCRIPT_TPL.replace('{logo_url}', logo_url)
        run_script(self, script_code, name="logo")
        print(f"[Browser {self.browser_id}] Injected logo.")


class AutodartsBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self._cleanup_started = False
        self.browsers = []
        self.init_ui()
        self.load_pages()
        self.init_refresh_timer()

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
        browser1 = BrowserView(1, url1, self)
        self.browsers.append(browser1)
        self.layout.addWidget(browser1)

        # Create Browser 2 if enabled
        if config.browser_count >= 2:
            url2 = config.get_board_url(2)
            browser2 = BrowserView(2, url2, self)
            self.browsers.append(browser2)
            self.layout.addWidget(browser2)

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
            print(f"[INFO] Auto-refresh enabled. Interval: {interval_min} minutes.")

    def cleanup(self):
        if self._cleanup_started:
            return
        self._cleanup_started = True

        print("[INFO] Cleaning up resources...")
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



class ConfigFileEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == str(CONFIG_PATH):
            print("config.ini has been modified, restarting application...")
            QApplication.instance().quit()
            # A small delay to ensure cleanup before execv
            QTimer.singleShot(250, lambda: os.execv(
                sys.executable, ['python'] + sys.argv))


def main():
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

    observer = Observer()
    event_handler = ConfigFileEventHandler()
    observer.schedule(event_handler, path=APP_DIR, recursive=False)
    observer.start()

    try:
        sys.exit(app.exec())
    finally:
        if observer.is_alive():
            observer.stop()
            observer.join()


if __name__ == "__main__":
    main()

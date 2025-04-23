import sys
import os
import configparser
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
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
import time

config = configparser.ConfigParser()
working_path, filename = os.path.split(os.path.abspath(__file__))
config_path = os.path.join(working_path, "config.ini")
config.read("config.ini")

url1 = f'https://play.autodarts.io/boards/{
    config.get("boards", "board1_id")}/follow'
url2 = f'https://play.autodarts.io/boards/{
    config.get("boards", "board2_id")}/follow'

css_style = config.getboolean("style", "activate")
browsers = config.getint("main", "browsers")
cache_dir = config.get("main", "cachedir")

logos_enable = config.getboolean("logos", "enable")
logos_local = config.getboolean("logos", "local")
logo = config.get("logos", "logo")

autologin = config.getboolean("autologin", "enable")
max_logins = config.getint("autologin", "versuche")
username = config.get("autologin", "username")
passwort = config.get("autologin", "passwort")

logins_1 = 0
logins_2 = 0

# Globale Variable für das Fenster
window = None

if autologin:
    LOGINSCRIPT = f"""
    try {{
        const observer = new MutationObserver(() => {{
            let user = document.querySelector('#username');
            let pass = document.querySelector('#password');
            let rmb = document.querySelector('input[id="rememberMe"]');
            let btn = document.querySelector('input[id="kc-login"]');
            if (user && pass && rmb && btn) {{
                console.log('Benötigte Felder gefunden, Autologin wird ausgeführt.');
                user.value = '{username}';
                pass.value = '{passwort}';
                rmb.checked = true;
                btn.click();
                observer.disconnect(); // Beobachtung stoppen
            }}
        }});

        observer.observe(document.body, {{ childList: true, subtree: true }});
    }} catch (error) {{
        console.error('Fehler im Autologin-Skript:', error);
    }}
    """

if css_style and logos_enable and logos_local:
    from http_server import ServeDirectoryWithHTTP

    ServeDirectoryWithHTTP()


def insert_logo(view, name):
    if logos_local:
        logo_url = f"http://localhost:3344/{logo}"
    else:
        logo_url = logo
    print(f"Logofile: {logo_url}")
    LOGO_SCRIPT = f"""
    try{{
    (function() {{
        let img = document.createElement('img');
        img.src ='{logo_url}';
        img.classList.add("logo-bottom-right");
        document.body.appendChild(img);
    }})()
    }}
    catch(error)
    {{
    console.log('Mixed Content');
    }}
    """

    script = QWebEngineScript()
    view.page().runJavaScript(LOGO_SCRIPT, QWebEngineScript.ApplicationWorld)
    script.setName(name)
    script.setSourceCode(LOGO_SCRIPT)
    script.setInjectionPoint(QWebEngineScript.DocumentReady)
    script.setRunsOnSubFrames(True)
    script.setWorldId(QWebEngineScript.ApplicationWorld)
    view.page().scripts().insert(script)


def injectCSS(view, path, name):
    path = QFile(path)
    if not path.open(QFile.ReadOnly | QFile.Text):
        return
    css = path.readAll().data().decode("utf-8")
    SCRIPT = """
    try
    {
    (function() {
    css = document.createElement('style');
    css.type = 'text/css';
    css.id = "%s";
    document.head.appendChild(css);
    css.innerText = `%s`;
    })()
    }
    catch(error)
    {
    console.log('mixed content');
    }
    """ % (
        name,
        css,
    )

    script = QWebEngineScript()
    view.page().runJavaScript(SCRIPT, QWebEngineScript.ApplicationWorld)
    script.setName(name)
    script.setSourceCode(SCRIPT)
    script.setInjectionPoint(QWebEngineScript.DocumentReady)
    script.setRunsOnSubFrames(True)
    script.setWorldId(QWebEngineScript.ApplicationWorld)
    view.page().scripts().insert(script)


class ConfigFileEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == config_path:
            print("config.ini wurde geändert, starte das Programm neu...")
            os.execv(sys.executable, ['python'] + sys.argv)


def start_config_watcher():
    event_handler = ConfigFileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=working_path, recursive=False)
    observer.start()
    return observer


class AutodartsBrowser(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(AutodartsBrowser, self).__init__(*args, **kwargs)
        self.initUi()
        self.loadPages()

    def initUi(self):
        self.window = QWidget()
        self.window.setWindowTitle("Autodarts Webbrowser")
        self.window.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.window.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.window.setStyleSheet("background-color: rgb(0, 0, 0);")

        # TODO Auswahl des Bildschirms implementieren
        """ self.screens = app.screens()
        print(self.screens)
        self.window.setScreen(self.screens[0]) """

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Setup Browser 1
        self.browser1 = QWebEngineView(self)
        self.profile1 = QWebEngineProfile("browser-1", self.browser1)
        self.profile1.setPersistentStoragePath(
            os.getcwd() + cache_dir + ("browser1"))
        self.webpage1 = QWebEnginePage(self.profile1, self.browser1)
        self.webpage1.loadFinished.connect(self._on_Load_Finished_1)
        self.webpage1.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ShowScrollBars, False
        )
        self.browser1.setPage(self.webpage1)
        self.layout.addWidget(self.browser1)

        # schwarzer Balken zwischen beiden Browsern
        """ self.frame = QFrame(self)
        self.frame.setObjectName("frame")
        self.frame.setMaximumSize(QSize(16777215, 20))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)

        self.layout.addWidget(self.frame) """

        # Setup Browser 2
        if browsers >= 2:
            self.browser2 = QWebEngineView(self)
            self.profile2 = QWebEngineProfile("browser-2", self.browser2)
            self.profile2.setPersistentStoragePath(
                os.getcwd() + cache_dir + ("browser2")
            )
            self.webpage2 = QWebEnginePage(self.profile2, self.browser2)
            self.webpage2.loadFinished.connect(self._on_Load_Finished_2)
            self.webpage2.settings().setAttribute(
                QWebEngineSettings.WebAttribute.ShowScrollBars, False
            )
            self.browser2.setPage(self.webpage2)
            self.layout.addWidget(self.browser2)

    def loadPages(self):
        self.browser1.page().setUrl(QUrl(url1))
        if browsers >= 2:
            self.browser2.page().setUrl(QUrl(url2))

    def showWindow(self):
        self.window.setLayout(self.layout)
        self.window.showFullScreen()

    def _login_browser1(self):
        global logins_1
        logins_1 += 1
        print(
            f"[Browser 1] Nicht eingelogt - Versuche Login {logins_1}/{max_logins}")
        self.browser1.page().runJavaScript(
            LOGINSCRIPT, QWebEngineScript.ApplicationWorld
        )

    def _login_browser2(self):
        global logins_2
        logins_2 += 1
        print(
            f"[Browser 2] Nicht eingelogt - Versuche Login {logins_2}/{max_logins}")
        self.browser2.page().runJavaScript(
            LOGINSCRIPT, QWebEngineScript.ApplicationWorld
        )

    def _on_Load_Finished_1(self, ok):
        if self.browser1.url().toString().split("#")[0] == url1:
            if ok and css_style:
                injectCSS(self.browser1, os.getcwd() +
                          "/style.css", "injectedCSS")
                if logos_enable:
                    insert_logo(self.browser1, "logo")
        else:
            if ok and autologin and logins_1 < max_logins:
                self._login_browser1()
            elif autologin and logins_1 >= max_logins:
                print("[Browser 1] Maximale Anzahl an Loginversuche erreicht")
            elif not autologin:
                print("[Browser 1] Autologin deaktiviert")

    def _on_Load_Finished_2(self, ok):
        if self.browser2.url().toString().split("#")[0] == url2:
            if ok and css_style:
                injectCSS(self.browser2, os.getcwd() +
                          "/style.css", "injectedCSS")
                if logos_enable:
                    insert_logo(self.browser2, "logo")
        else:
            if ok and autologin and logins_2 < max_logins:
                self._login_browser2()
            elif autologin and logins_2 >= max_logins:
                print("[Browser 2] Maximale Anzahl an Loginversuche erreicht")
            elif not autologin:
                print("[Browser 2] Autologin deaktiviert")


cleanup_executed = False  # Flag, um doppelte Bereinigung zu verhindern

# Bereinigung der Ressourcen


def cleanup():
    global cleanup_executed
    if cleanup_executed:
        return
    cleanup_executed = True

    print("[INFO] Bereinige Ressourcen vor dem Beenden...")

    if hasattr(window, 'browser1'):
        window.browser1.close()
        window.browser1.setPage(None)
        window.webpage1.deleteLater()
        window.browser1.deleteLater()
        window.profile1.deleteLater()

    if hasattr(window, 'browser2'):
        window.browser2.close()
        window.browser2.setPage(None)
        window.webpage2.deleteLater()
        window.browser2.deleteLater()
        window.profile2.deleteLater()

    print("[INFO] Ressourcenbereinigung abgeschlossen.")

    # Verzögerung hinzufügen, um die Ereignisschleife laufen zu lassen
    QTimer.singleShot(100, QApplication.quit)


def main():
    global window  # Zugriff auf die globale Variable
    app = QApplication(sys.argv)

    app.aboutToQuit.connect(cleanup)

    observer = start_config_watcher()
    window = AutodartsBrowser()
    window.showWindow()
    try:
        sys.exit(app.exec())
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()

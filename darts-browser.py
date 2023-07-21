import sys
import os
import configparser
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QUrl, QFile, Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEnginePage,
    QWebEngineScript,
    QWebEngineSettings,
)

config = configparser.ConfigParser()
config.read("config.ini")

url1 = f'https://autodarts.io/boards/{config.get("boards", "board1_id")}/follow'
url2 = f'https://autodarts.io/boards/{config.get("boards", "board2_id")}/follow'

css_style = config.getboolean("style", "activate")
browsers = config.getint("main", "browsers")
cache_dir = config.get("main", "cachedir")


def injectCSS(view, path, name):
    path = QFile(path)
    if not path.open(QFile.ReadOnly | QFile.Text):
        return
    css = path.readAll().data().decode("utf-8")
    SCRIPT = """
    (function() {
    css = document.createElement('style');
    css.type = 'text/css';
    css.id = "%s";
    document.head.appendChild(css);
    css.innerText = `%s`;
    })()
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
        self.profile1.setPersistentStoragePath(os.getcwd() + cache_dir + ("browser1"))
        self.webpage1 = QWebEnginePage(self.profile1, self.browser1)
        self.webpage1.loadFinished.connect(self._on_Load_Finished_1)
        self.webpage1.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ShowScrollBars, False
        )
        self.browser1.setPage(self.webpage1)
        self.layout.addWidget(self.browser1)

        # Setup Browser 2
        if browsers >= 2:
            self.browser2 = QWebEngineView(self)
            self.profile2 = QWebEngineProfile("browser-2", self.browser2)
            self.profile2.setPersistentStoragePath(
                os.getcwd() + cache_dir + ("browser2")
            )
            self.webpage2 = QWebEnginePage(self.profile2, self.browser2)
            self.webpage2.loadFinished.connect(self._on_Load_Finished_2)
            self.browser2.setPage(self.webpage2)
            self.layout.addWidget(self.browser2)

    def loadPages(self):
        self.browser1.page().setUrl(QUrl(url1))
        if browsers >= 2:
            self.browser2.page().setUrl(QUrl(url2))

    def showWindow(self):
        self.window.setLayout(self.layout)
        self.window.showFullScreen()

    def _on_Load_Finished_1(self, ok):
        if ok and css_style:
            injectCSS(self.browser1, os.getcwd() + "/style.css", "injectedCSS")

    def _on_Load_Finished_2(self, ok):
        if ok and css_style:
            injectCSS(self.browser2, os.getcwd() + "/style.css", "injectedCSS")


# FIXME
# Release of profile requested but WebEnginePage still not deleted. Expect troubles !
# https://sdestackoverflow.com/questions/64719361/closing-qwebengineview-warns-release-of-profile-requested-but-webenginepage-sti


def main():
    app = QApplication(sys.argv)
    window = AutodartsBrowser()
    window.showWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

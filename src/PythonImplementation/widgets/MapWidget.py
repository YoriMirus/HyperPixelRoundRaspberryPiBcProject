import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFrame, QLabel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QUrl, Signal, Qt
import os

class MapWidget(QWidget):
    mapReady = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedSize(480, 480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---- Top blank draggable area ----
        self.topBlank = QFrame()
        self.topBlank.setFixedHeight(80)
        self.topBlank.setStyleSheet("background: transparent;")

        # Layout inside the top blank area
        topLayout = QVBoxLayout(self.topBlank)
        topLayout.setContentsMargins(0, 0, 0, 0)

        # ---- Arrow label ----
        self.arrowLabel = QLabel("▲")
        self.arrowLabel.setAlignment(Qt.AlignCenter)
        self.arrowLabel.setStyleSheet("""
            font-size: 24px;
            color: white;
        """)
        topLayout.addWidget(self.arrowLabel)

        layout.addWidget(self.topBlank)

        # ---- Map area ----
        self.web = QWebEngineView()

        settings = self.web.page().profile().settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

        html_path = os.path.abspath("assets/map.html")
        self.web.load(QUrl.fromLocalFile(html_path))

        self.web.loadFinished.connect(self._on_load_finished)
        self.map_ready = False

        layout.addWidget(self.web)

    def old__init__(self):
        super().__init__()
        self.setFixedSize(480,480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        self.web = QWebEngineView()

        # IMPORTANT: allow local HTML to load CDN resources
        settings = self.web.page().profile().settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

        html_path = os.path.abspath("assets/map.html")
        self.web.load(QUrl.fromLocalFile(html_path))

        # Wait until HTML is fully loaded
        self.web.loadFinished.connect(self._on_load_finished)

        layout.addWidget(self.web)
        self.map_ready = False

    def _on_load_finished(self):
        print("Map page loaded.")
        self.map_ready = True
        self.mapReady.emit()

    def setMapPosition(self, lat, lon, zoom=None):
        if not self.map_ready:
            print("Map not ready yet.")
            return

        if zoom is None:
            js = f"map.setView([{lat}, {lon}]);"
        else:
            js = f"map.setView([{lat}, {lon}], {zoom});"

        self.web.page().runJavaScript(js)
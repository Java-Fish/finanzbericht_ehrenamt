# -*- coding: utf-8 -*-
"""
Über-Dialog der Anwendung
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import sys
import os
from pathlib import Path

from ..utils.icon_helper import get_app_pixmap, app_icon_exists


class AboutDialog(QDialog):
    """Dialog mit Informationen über die Anwendung"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    @staticmethod
    def _get_version() -> str:
        """Ermittelt die Anwendungs-Version.

        Priorität:
        1. Umgebungsvariable APP_VERSION (z.B. beim Build gesetzt)
        2. Datei "version" im Projektwurzelverzeichnis
        3. Fallback "0.0.0"
        """
        env_v = os.getenv("APP_VERSION")
        if env_v:
            return env_v.strip()

        try:
            # Projektwurzel: this_file -> dialogs -> src -> root
            root = Path(__file__).resolve().parents[2]
            version_file = root / "version"
            if version_file.is_file():
                content = version_file.read_text(encoding="utf-8").strip().splitlines()
                if content:
                    v = content[0].strip()
                    if v:
                        return v
        except Exception:
            pass
        return "0.0.0"
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        self.setWindowTitle("Über Finanzauswertung Ehrenamt")
        self.setFixedSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # App Icon/Logo
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if app_icon_exists():
            scaled_pixmap = get_app_pixmap(64)
            icon_label.setPixmap(scaled_pixmap)
            icon_label.setFixedSize(64, 64)
        else:
            icon_label.setText("📊")
            icon_label.setStyleSheet("font-size: 48px; margin: 10px;")
        layout.addWidget(icon_label)

        # App Name
        name_label = QLabel("Finanzauswertung Ehrenamt")
        name_font = QFont()
        name_font.setPointSize(18)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Version
        version_label = QLabel(f"Version {self._get_version()}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666666; margin-bottom: 10px;")
        layout.addWidget(version_label)

        # Beschreibung
        description = QTextEdit()
        description.setReadOnly(True)
        description.setMaximumHeight(150)
        description.setHtml(
            """
        <p><b>Eine benutzerfreundliche Desktop-Anwendung zur Analyse von Finanzdaten für ehrenamtliche Organisationen.</b></p>
        <p><b>Features:</b></p>
        <ul>
        <li>Drag & Drop Interface für Excel, LibreOffice Calc und CSV-Dateien</li>
        <li>Plattformübergreifend (macOS, Windows, Linux)</li>
        <li>Mehrsprachige Unterstützung (Deutsch, Englisch)</li>
        <li>Flexible Spalten-Zuordnungen</li>
        <li>Organisationsprofile mit Logo-Unterstützung</li>
        </ul>
            """
        )
        layout.addWidget(description)

        # Lizenz-Information
        license_frame = QFrame()
        license_frame.setFrameStyle(QFrame.Shape.Box)
        license_frame.setStyleSheet("background-color: #f5f5f5; padding: 10px;")
        license_layout = QVBoxLayout(license_frame)

        license_title = QLabel("Lizenz")
        license_font = QFont()
        license_font.setBold(True)
        license_title.setFont(license_font)
        license_layout.addWidget(license_title)

        license_text = QLabel(
            "Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)\\nNicht-kommerzielle Nutzung erlaubt. Namensnennung erforderlich."
        )
        license_text.setWordWrap(True)
        license_text.setStyleSheet("color: #555555;")
        license_layout.addWidget(license_text)
        layout.addWidget(license_frame)

        # Technische Informationen
        tech_info = QLabel(f"Python {sys.version.split()[0]} • PySide6")
        tech_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tech_info.setStyleSheet("color: #888888; font-size: 11px; margin-top: 10px;")
        layout.addWidget(tech_info)

        # OK Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("OK")
        ok_button.setMinimumWidth(80)
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

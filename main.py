#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finanzauswertung für Ehrenamtliche Organisationen
Lizenz: CC BY-NC 4.0
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLocale, QSettings

from src.main_window import MainWindow
from src.utils.translations import setup_translations
from src.utils.icon_helper import get_app_icon


def main():
    """Hauptfunktion der Anwendung"""
    app = QApplication(sys.argv)
    
    # Anwendungsmetadaten setzen
    app.setApplicationName("Finanzauswertung Ehrenamt")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Ehrenamt Tools")
    app.setOrganizationDomain("ehrenamt-tools.org")
    
    # Icon setzen
    app.setWindowIcon(get_app_icon())
    
    # Übersetzungen laden
    translator = setup_translations(app)
    
    # Hauptfenster erstellen und anzeigen
    window = MainWindow()
    window.show()
    
    # Anwendung starten
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

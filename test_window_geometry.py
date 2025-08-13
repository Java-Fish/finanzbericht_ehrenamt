#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für Fenstergrößen-Persistierung
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings, QRect
from src.main_window import MainWindow
from src.settings.settings_window import SettingsWindow

def test_window_geometry_persistence():
    """Testet die Persistierung von Fenstergrößen"""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    print("=== Fenstergrößen-Persistierung Test ===")
    
    # Temporäre Settings verwenden
    temp_settings = QSettings("TestOrg", "WindowGeometryTest")
    temp_settings.clear()  # Sauberer Start
    
    # Test 1: Hauptfenster
    print("\n1. Hauptfenster-Geometrie testen...")
    
    # Erstes Hauptfenster erstellen
    main_window = MainWindow()
    main_window.settings = temp_settings
    
    # Benutzerdefinierte Größe setzen
    test_geometry = QRect(100, 100, 1200, 800)
    main_window.setGeometry(test_geometry)
    
    # Geometrie speichern (simuliert closeEvent)
    main_window.settings.setValue("geometry", main_window.saveGeometry())
    main_window.settings.sync()
    
    print(f"   Gesetzt: {test_geometry}")
    print(f"   Gespeichert: Ja")
    
    # Neues Hauptfenster erstellen und laden
    new_main_window = MainWindow()
    new_main_window.settings = temp_settings
    new_main_window.load_settings()
    
    # Geometrie vergleichen
    loaded_geometry = new_main_window.geometry()
    print(f"   Geladen: {loaded_geometry}")
    
    main_geometry_ok = (loaded_geometry.width() == test_geometry.width() and 
                       loaded_geometry.height() == test_geometry.height())
    
    print(f"   Hauptfenster-Geometrie korrekt: {main_geometry_ok}")
    
    # Test 2: Einstellungsfenster
    print("\n2. Einstellungsfenster-Geometrie testen...")
    
    # Erstes Einstellungsfenster erstellen
    settings_window = SettingsWindow()
    settings_window.settings = temp_settings
    
    # Benutzerdefinierte Größe setzen
    settings_test_geometry = QRect(200, 200, 900, 650)
    settings_window.setGeometry(settings_test_geometry)
    
    # Geometrie speichern (simuliert closeEvent)
    settings_window.settings.setValue("settings_window/geometry", settings_window.saveGeometry())
    settings_window.settings.sync()
    
    print(f"   Gesetzt: {settings_test_geometry}")
    print(f"   Gespeichert: Ja")
    
    # Neues Einstellungsfenster erstellen und laden
    new_settings_window = SettingsWindow()
    new_settings_window.settings = temp_settings
    new_settings_window.load_settings()
    
    # Geometrie vergleichen
    settings_loaded_geometry = new_settings_window.geometry()
    print(f"   Geladen: {settings_loaded_geometry}")
    
    settings_geometry_ok = (settings_loaded_geometry.width() == settings_test_geometry.width() and 
                           settings_loaded_geometry.height() == settings_test_geometry.height())
    
    print(f"   Einstellungsfenster-Geometrie korrekt: {settings_geometry_ok}")
    
    # Test 3: Unabhängige Settings-Keys prüfen
    print("\n3. Settings-Keys prüfen...")
    
    main_geometry_key = temp_settings.value("geometry")
    settings_geometry_key = temp_settings.value("settings_window/geometry")
    
    print(f"   Hauptfenster-Key vorhanden: {main_geometry_key is not None}")
    print(f"   Einstellungen-Key vorhanden: {settings_geometry_key is not None}")
    print(f"   Keys sind unterschiedlich: {main_geometry_key != settings_geometry_key}")
    
    # Gesamtergebnis
    all_tests_ok = (main_geometry_ok and settings_geometry_ok and 
                   main_geometry_key is not None and settings_geometry_key is not None and
                   main_geometry_key != settings_geometry_key)
    
    if all_tests_ok:
        print("\n✅ FENSTERGRÖSSEN-PERSISTIERUNG ERFOLGREICH!")
        print("   - Hauptfenster speichert und lädt Geometrie")
        print("   - Einstellungsfenster speichert und lädt Geometrie")
        print("   - Beide Fenster verwenden separate Settings-Keys")
    else:
        print("\n❌ PROBLEME BEI FENSTERGRÖSSEN-PERSISTIERUNG!")
        if not main_geometry_ok:
            print("   - Hauptfenster-Geometrie nicht korrekt")
        if not settings_geometry_ok:
            print("   - Einstellungsfenster-Geometrie nicht korrekt")
    
    # Aufräumen
    temp_settings.clear()
    
    print("\n=== Test abgeschlossen ===")

if __name__ == "__main__":
    test_window_geometry_persistence()

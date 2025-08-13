#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Script für die Finanzauswertung Ehrenamt Anwendung
"""

import sys
import os

# Füge den src-Pfad zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Testet ob alle wichtigen Module importiert werden können"""
    print("Teste Imports...")
    
    try:
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6 erfolgreich importiert")
    except ImportError as e:
        print(f"❌ PySide6 Import fehlgeschlagen: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas erfolgreich importiert")
    except ImportError as e:
        print(f"❌ pandas Import fehlgeschlagen: {e}")
        return False
    
    try:
        import openpyxl
        print("✅ openpyxl erfolgreich importiert")
    except ImportError as e:
        print(f"❌ openpyxl Import fehlgeschlagen: {e}")
        return False
    
    try:
        import chardet
        print("✅ chardet erfolgreich importiert")
    except ImportError as e:
        print(f"❌ chardet Import fehlgeschlagen: {e}")
        return False
    
    return True


def test_module_imports():
    """Testet ob die eigenen Module importiert werden können"""
    print("\nTeste eigene Module...")
    
    try:
        from src.main_window import MainWindow
        print("✅ MainWindow erfolgreich importiert")
    except ImportError as e:
        print(f"❌ MainWindow Import fehlgeschlagen: {e}")
        return False
    
    try:
        from src.widgets.file_drop_area import FileDropArea
        print("✅ FileDropArea erfolgreich importiert")
    except ImportError as e:
        print(f"❌ FileDropArea Import fehlgeschlagen: {e}")
        return False
    
    try:
        from src.settings.settings_window import SettingsWindow
        print("✅ SettingsWindow erfolgreich importiert")
    except ImportError as e:
        print(f"❌ SettingsWindow Import fehlgeschlagen: {e}")
        return False
    
    try:
        from src.utils.file_handler import FileHandler
        print("✅ FileHandler erfolgreich importiert")
    except ImportError as e:
        print(f"❌ FileHandler Import fehlgeschlagen: {e}")
        return False
    
    return True


def test_gui_creation():
    """Testet ob die GUI erstellt werden kann"""
    print("\nTeste GUI-Erstellung...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.main_window import MainWindow
        
        # QApplication erstellen (notwendig für GUI-Tests)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Hauptfenster erstellen
        window = MainWindow()
        print("✅ Hauptfenster erfolgreich erstellt")
        
        # Fenster wieder schließen
        window.close()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI-Erstellung fehlgeschlagen: {e}")
        return False


def main():
    """Hauptfunktion des Test-Scripts"""
    print("=" * 50)
    print("  Finanzauswertung Ehrenamt - Tests")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Import-Tests
    if not test_imports():
        all_tests_passed = False
    
    # Module-Tests
    if not test_module_imports():
        all_tests_passed = False
    
    # GUI-Tests
    if not test_gui_creation():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ Alle Tests erfolgreich!")
        print("\nDie Anwendung ist bereit zum Start:")
        print("  python main.py")
    else:
        print("❌ Einige Tests sind fehlgeschlagen!")
        print("\nBitte überprüfen Sie die Installation:")
        print("  pip install -r requirements.txt")
    print("=" * 50)
    
    return 0 if all_tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())

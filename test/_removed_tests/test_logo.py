#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script für Logo-Integration
"""

import sys
import os

# Pfad für imports hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# PySide6 Application für GUI-Tests
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication

from src.utils.icon_helper import app_icon_exists, get_icon_path, get_app_icon, get_app_pixmap

def test_logo_integration():
    """Testet die Logo-Integration"""
    print("=== Logo-Integrations-Test ===")
    
    # QApplication für GUI-Tests erstellen
    if not QCoreApplication.instance():
        app = QApplication(sys.argv)
    
    # 1. Icon-Pfad prüfen
    icon_path = get_icon_path("app_icon.png")
    print(f"Icon-Pfad: {icon_path}")
    print(f"Icon existiert: {os.path.exists(icon_path)}")
    
    # 2. Helper-Funktionen testen
    print(f"app_icon_exists(): {app_icon_exists()}")
    
    # 3. Icon laden
    try:
        icon = get_app_icon()
        print(f"Icon geladen: {not icon.isNull()}")
    except Exception as e:
        print(f"Fehler beim Icon-Laden: {e}")
        return False
    
    # 4. Pixmap laden
    pixmap = get_app_pixmap(80)
    print(f"Pixmap geladen: {not pixmap.isNull()}")
    print(f"Pixmap Größe: {pixmap.width()}x{pixmap.height()}")
    
    print("\n=== Test abgeschlossen ===")

if __name__ == "__main__":
    test_logo_integration()

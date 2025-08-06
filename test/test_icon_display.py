#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Icon Test - Prüft Icon-Verfügbarkeit ohne GUI-Display
"""

import sys
import os
from pathlib import Path

def test_icon_availability():
    """Testet Icon-Verfügbarkeit ohne GUI"""
    print("🎨 Teste Icon-Verfügbarkeit...")
    
    try:
        # PySide6 imports
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QPixmap, QIcon
        
        # Lokale imports  
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.utils.icon_helper import get_app_icon, get_app_pixmap, app_icon_exists, get_icon_path
        
        # QApplication für Qt-Funktionalität (aber ohne GUI)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setQuitOnLastWindowClosed(True)
        
        # Icon-Tests ohne Fenster-Display
        print("📋 Icon-Verfügbarkeits-Tests:")
        
        # Test 1: Icon-Pfad
        icon_path = get_icon_path('app_icon.png')
        print(f"  Icon-Pfad: {icon_path}")
        
        # Test 2: Icon-Existenz
        exists = app_icon_exists()
        print(f"  Icon existiert: {exists}")
        
        # Test 3: Icon laden ohne Display
        icon = get_app_icon()
        icon_loaded = not icon.isNull()
        print(f"  Icon geladen: {icon_loaded}")
        
        # Test 4: Pixmap-Test ohne Display
        pixmap = get_app_pixmap(64)
        pixmap_loaded = not pixmap.isNull()
        pixmap_size = f"{pixmap.size().width()}x{pixmap.size().height()}" if pixmap_loaded else "N/A"
        print(f"  Pixmap geladen: {pixmap_loaded}")
        print(f"  Pixmap Größe: {pixmap_size}")
        
        # Erfolg bewerten
        if exists and icon_loaded and pixmap_loaded:
            print("✅ Alle Icon-Tests erfolgreich")
            return True
        else:
            print("❌ Ein oder mehrere Icon-Tests fehlgeschlagen")
            return False
            
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("Stelle sicher, dass PySide6 installiert ist: pip install PySide6")
        return False
    except Exception as e:
        print(f"❌ Fehler beim Icon-Test: {e}")
        return False

def main():
    """Hauptfunktion"""
    return test_icon_availability()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

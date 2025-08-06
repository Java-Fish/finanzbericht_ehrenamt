#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der Kontostand-Funktionalität
"""

import sys
import os
from PySide6.QtCore import QSettings

# Projektpfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_balance_settings():
    """Testet die Kontostand-Einstellungen"""
    settings = QSettings()
    
    print("=== Kontostand-Einstellungen Test ===")
    
    # Aktueller Wert
    current_balance = settings.value("opening_balance", 0.0, type=float)
    print(f"Aktueller Anfangskontostand: {current_balance:.2f} €")
    
    # Test-Wert setzen
    test_balance = 1500.50
    settings.setValue("opening_balance", test_balance)
    print(f"Test-Wert gesetzt: {test_balance:.2f} €")
    
    # Wert wieder laden
    loaded_balance = settings.value("opening_balance", 0.0, type=float)
    print(f"Geladener Wert: {loaded_balance:.2f} €")
    
    # Vergleichen
    if abs(loaded_balance - test_balance) < 0.01:
        print("✅ Speichern und Laden funktioniert korrekt!")
    else:
        print("❌ Fehler beim Speichern/Laden!")
    
    # Originalen Wert wiederherstellen
    settings.setValue("opening_balance", current_balance)
    print(f"Original-Wert wiederhergestellt: {current_balance:.2f} €")
    
    print("\n=== Test abgeschlossen ===")

if __name__ == "__main__":
    test_balance_settings()

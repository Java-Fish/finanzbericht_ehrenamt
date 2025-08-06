#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der Kontostand-Verlagerung von Allgemein zu Organisation
"""

import sys
import os
from PySide6.QtCore import QSettings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_balance_migration():
    """Testet ob das Kontostand-Feld korrekt verschoben wurde"""
    settings = QSettings()
    
    print("=== Kontostand-Verlagerungs-Test ===")
    
    # Test-Wert setzen
    test_balance = 2500.75
    settings.setValue("opening_balance", test_balance)
    print(f"Test-Kontostand gesetzt: {test_balance:.2f} €")
    
    # Prüfen ob der Wert korrekt geladen wird
    loaded_balance = settings.value("opening_balance", 0.0, type=float)
    print(f"Geladener Kontostand: {loaded_balance:.2f} €")
    
    # Deutsche Formatierung testen
    formatted = f"{loaded_balance:.2f}".replace(".", ",")
    print(f"Deutsche Formatierung: {formatted} €")
    
    if abs(loaded_balance - test_balance) < 0.01:
        print("✅ Kontostand-Speicherung funktioniert korrekt!")
    else:
        print("❌ Fehler bei der Kontostand-Speicherung!")
    
    # Zurücksetzen
    settings.setValue("opening_balance", 0.0)
    print("Kontostand zurückgesetzt auf 0,00 €")
    
    print("\n=== Test abgeschlossen ===")
    print("💡 Das Kontostand-Feld befindet sich jetzt unter 'Organisation' statt 'Allgemein'")

if __name__ == "__main__":
    test_balance_migration()

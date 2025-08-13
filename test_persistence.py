#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript für Account-Mapping Persistierung
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from src.settings.account_mapping import AccountMappingTab
from src.settings.super_group_mapping import SuperGroupMappingTab
import tempfile
import json

def test_persistence():
    """Testet die Persistierung von Account-Mappings"""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Temporäre Settings-Datei verwenden
    temp_settings = QSettings("TestOrg", "TestApp")
    
    print("=== Account Mapping Persistierung Test ===")
    
    # Test 1: Account Mapping Tab erstellen und Daten hinzufügen
    print("\n1. AccountMappingTab erstellen...")
    mapping_tab = AccountMappingTab()
    mapping_tab.settings = temp_settings
    
    # Test-Daten hinzufügen
    test_accounts = {
        "4000": "Umsatzerlöse",
        "5000": "Wareneinsatz", 
        "6000": "Löhne und Gehälter"
    }
    
    test_mappings = {
        "4000": "Erträge",
        "5000": "Materialaufwand",
        "6000": "Personalkosten"
    }
    
    print("2. Test-Daten hinzufügen...")
    for account, name in test_accounts.items():
        mapping_tab.account_names[account] = name
        
    for account, group in test_mappings.items():
        mapping_tab.account_mappings[account] = group
    
    # Einstellungen speichern
    print("3. Einstellungen speichern...")
    mapping_tab.save_settings()
    
    print(f"   Gespeicherte Mappings: {len(mapping_tab.account_mappings)}")
    print(f"   Gespeicherte Namen: {len(mapping_tab.account_names)}")
    
    # Test 2: Neue Instanz erstellen und laden
    print("\n4. Neue Instanz erstellen und laden...")
    new_mapping_tab = AccountMappingTab()
    new_mapping_tab.settings = temp_settings
    new_mapping_tab.load_settings()
    
    print(f"   Geladene Mappings: {len(new_mapping_tab.account_mappings)}")
    print(f"   Geladene Namen: {len(new_mapping_tab.account_names)}")
    
    # Verifikation
    print("\n5. Verifikation...")
    mappings_match = new_mapping_tab.account_mappings == test_mappings
    names_match = new_mapping_tab.account_names == test_accounts
    
    print(f"   Mappings korrekt geladen: {mappings_match}")
    print(f"   Namen korrekt geladen: {names_match}")
    
    if mappings_match and names_match:
        print("\n✅ PERSISTIERUNG TEST ERFOLGREICH!")
    else:
        print("\n❌ PERSISTIERUNG TEST FEHLGESCHLAGEN!")
        print(f"   Erwartete Mappings: {test_mappings}")
        print(f"   Geladene Mappings: {new_mapping_tab.account_mappings}")
        print(f"   Erwartete Namen: {test_accounts}")
        print(f"   Geladene Namen: {new_mapping_tab.account_names}")
    
    # Test 3: Liste-Population testen
    print("\n6. Listen-Population testen...")
    
    # Accounts-Liste sollte mit bekannten Konten gefüllt sein
    accounts_count = new_mapping_tab.accounts_list.count()
    print(f"   Anzahl Einträge in accounts_list: {accounts_count}")
    
    if accounts_count == len(test_accounts):
        print("   ✅ Liste korrekt befüllt")
    else:
        print("   ❌ Liste nicht korrekt befüllt")
    
    # Settings aufräumen
    temp_settings.clear()
    
    print("\n=== Test abgeschlossen ===")

if __name__ == "__main__":
    test_persistence()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript für CSV-Import mit Obergruppen
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from src.settings.account_mapping import AccountMappingTab
from src.settings.super_group_mapping import SuperGroupMappingTab
from src.settings.settings_window import SettingsWindow
import csv
import tempfile

def test_csv_import_with_supergroups():
    """Testet den CSV-Import mit Obergruppen-Zuordnung"""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    print("=== CSV Import mit Obergruppen Test ===")
    
    # Test-CSV erstellen
    test_csv_path = "test_import.csv"
    test_data = [
        ["Sachkontonr.", "Sachkonto", "BWA-Gruppe", "Obergruppe"],
        ["4000", "Umsatzerlöse", "Erträge", "Einnahmen"],
        ["5000", "Wareneinsatz", "Materialkosten", "Ausgaben"],
        ["6000", "Löhne", "Personalkosten", "Ausgaben"],
        ["7000", "Miete", "Bürokosten", "Verwaltung"]
    ]
    
    print("1. Test-CSV erstellen...")
    with open(test_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerows(test_data)
    
    print(f"   CSV erstellt: {test_csv_path}")
    
    # Settings Window erstellen (simuliert das Hauptfenster)
    print("2. SettingsWindow erstellen...")
    settings_window = SettingsWindow()
    
    # Temporary Settings verwenden
    temp_settings = QSettings("TestOrg", "TestApp")
    settings_window.account_mapping_tab.settings = temp_settings
    settings_window.super_group_mapping_tab.settings = temp_settings
    
    # Bestehende Settings leeren für sauberen Test
    settings_window.account_mapping_tab.reset_to_defaults()
    settings_window.super_group_mapping_tab.reset_to_defaults()
    
    # CSV-Datei programmatisch importieren
    print("3. CSV-Import simulieren...")
    account_tab = settings_window.account_mapping_tab
    super_tab = settings_window.super_group_mapping_tab
    
    # CSV lesen und manuell importieren (ohne GUI)
    imported_mappings = {}
    imported_names = {}
    imported_super_groups = {}
    
    with open(test_csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            sachkontonr = row['Sachkontonr.'].strip()
            sachkonto = row['Sachkonto'].strip()
            bwa_gruppe = row['BWA-Gruppe'].strip()
            obergruppe = row['Obergruppe'].strip()
            
            if sachkontonr and sachkonto:
                imported_names[sachkontonr] = sachkonto
            if sachkontonr and bwa_gruppe:
                imported_mappings[sachkontonr] = bwa_gruppe
            if bwa_gruppe and obergruppe and bwa_gruppe not in imported_super_groups:
                imported_super_groups[bwa_gruppe] = obergruppe
    
    # Daten in die Tabs einsetzen
    account_tab.account_names.update(imported_names)
    account_tab.account_mappings.update(imported_mappings)
    
    # Obergruppen aktualisieren
    settings_window.update_super_group_mappings(imported_super_groups)
    
    print(f"   Importierte Sachkonten: {len(imported_names)}")
    print(f"   Importierte BWA-Mappings: {len(imported_mappings)}")
    print(f"   Importierte Obergruppen: {len(imported_super_groups)}")
    
    # Verifikation
    print("4. Verifikation...")
    
    # Account Mappings prüfen
    expected_mappings = {
        "4000": "Erträge",
        "5000": "Materialkosten", 
        "6000": "Personalkosten",
        "7000": "Bürokosten"
    }
    
    expected_super_groups = {
        "Erträge": "Einnahmen",
        "Materialkosten": "Ausgaben",
        "Personalkosten": "Ausgaben", 
        "Bürokosten": "Verwaltung"
    }
    
    mappings_correct = account_tab.account_mappings == expected_mappings
    super_groups_correct = super_tab.super_group_mappings == expected_super_groups
    
    print(f"   BWA-Mappings korrekt: {mappings_correct}")
    print(f"   Obergruppen korrekt: {super_groups_correct}")
    
    if mappings_correct and super_groups_correct:
        print("\n✅ CSV IMPORT MIT OBERGRUPPEN ERFOLGREICH!")
    else:
        print("\n❌ CSV IMPORT MIT OBERGRUPPEN FEHLGESCHLAGEN!")
        print(f"   Erwartete BWA-Mappings: {expected_mappings}")
        print(f"   Aktuelle BWA-Mappings: {account_tab.account_mappings}")
        print(f"   Erwartete Obergruppen: {expected_super_groups}")
        print(f"   Aktuelle Obergruppen: {super_tab.super_group_mappings}")
    
    # Test 5: Persistierung nach Import testen
    print("\n5. Persistierung nach Import testen...")
    account_tab.save_settings()
    super_tab.save_settings()
    
    # Neue Instanzen erstellen und laden
    new_settings_window = SettingsWindow()
    new_settings_window.account_mapping_tab.settings = temp_settings
    new_settings_window.super_group_mapping_tab.settings = temp_settings
    new_settings_window.load_settings()
    
    new_mappings_correct = new_settings_window.account_mapping_tab.account_mappings == expected_mappings
    new_super_correct = new_settings_window.super_group_mapping_tab.super_group_mappings == expected_super_groups
    
    print(f"   Persistierte BWA-Mappings korrekt: {new_mappings_correct}")
    print(f"   Persistierte Obergruppen korrekt: {new_super_correct}")
    
    if new_mappings_correct and new_super_correct:
        print("   ✅ Persistierung erfolgreich")
    else:
        print("   ❌ Persistierung fehlgeschlagen")
    
    # Aufräumen
    os.unlink(test_csv_path)
    temp_settings.clear()
    
    print("\n=== Test abgeschlossen ===")

if __name__ == "__main__":
    test_csv_import_with_supergroups()

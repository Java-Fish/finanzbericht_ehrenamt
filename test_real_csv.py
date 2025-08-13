#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Test für echte BWA-Gruppen CSV
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

def test_real_bwa_csv():
    """Testet Import der echten BWA-Gruppen CSV"""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    print("=== Echter BWA-Gruppen CSV Import Test ===")
    
    csv_path = "testdata/bwa_gruppen_export.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV-Datei nicht gefunden: {csv_path}")
        return
    
    print(f"1. CSV-Datei gefunden: {csv_path}")
    
    # Settings Window erstellen
    settings_window = SettingsWindow()
    
    # Temporary Settings verwenden
    temp_settings = QSettings("TestOrg", "TestApp")
    settings_window.account_mapping_tab.settings = temp_settings
    settings_window.super_group_mapping_tab.settings = temp_settings
    
    # Bestehende Settings leeren
    settings_window.account_mapping_tab.reset_to_defaults()
    settings_window.super_group_mapping_tab.reset_to_defaults()
    
    # CSV lesen und analysieren
    print("2. CSV-Datei analysieren...")
    
    imported_mappings = {}
    imported_names = {}
    imported_super_groups = {}
    total_rows = 0
    
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            total_rows += 1
            sachkontonr = row.get('Sachkontonr.', '').strip()
            sachkonto = row.get('Sachkonto', '').strip()
            bwa_gruppe = row.get('BWA-Gruppe', '').strip()
            obergruppe = row.get('Obergruppe', '').strip()
            
            # Nur Zeilen mit Sachkontonummer verarbeiten
            if not sachkontonr:
                continue
                
            # Kontonummer normalisieren (S entfernen)
            if sachkontonr.startswith('S'):
                sachkontonr = sachkontonr[1:]
            
            if sachkonto:
                imported_names[sachkontonr] = sachkonto
            if bwa_gruppe:
                imported_mappings[sachkontonr] = bwa_gruppe
                # Obergruppen sammeln (eindeutig pro BWA-Gruppe)
                if obergruppe and bwa_gruppe not in imported_super_groups:
                    imported_super_groups[bwa_gruppe] = obergruppe
    
    print(f"   Gesamte Zeilen: {total_rows}")
    print(f"   Sachkonten mit Namen: {len(imported_names)}")
    print(f"   Sachkonten mit BWA-Gruppen: {len(imported_mappings)}")
    print(f"   Eindeutige BWA-Gruppen: {len(set(imported_mappings.values()))}")
    print(f"   BWA-Gruppen mit Obergruppen: {len(imported_super_groups)}")
    
    # 3. Import simulieren
    print("3. Import in die Anwendung...")
    
    account_tab = settings_window.account_mapping_tab
    super_tab = settings_window.super_group_mapping_tab
    
    # Daten einsetzen
    account_tab.account_names.update(imported_names)
    account_tab.account_mappings.update(imported_mappings)
    account_tab.save_settings()
    
    # Obergruppen über das Settings Window aktualisieren
    settings_window.update_super_group_mappings(imported_super_groups)
    
    # 4. Verifikation
    print("4. Verifikation...")
    
    saved_mappings = len(account_tab.account_mappings)
    saved_names = len(account_tab.account_names)
    saved_super_groups = len(super_tab.super_group_mappings)
    
    print(f"   Gespeicherte BWA-Mappings: {saved_mappings}")
    print(f"   Gespeicherte Sachkonten-Namen: {saved_names}")
    print(f"   Gespeicherte Obergruppen: {saved_super_groups}")
    
    # Liste population testen
    account_tab._populate_known_accounts()
    list_count = account_tab.accounts_list.count()
    print(f"   Einträge in Sachkonten-Liste: {list_count}")
    
    # 5. Neustart-Simulation
    print("5. Neustart simulieren...")
    
    new_settings_window = SettingsWindow()
    new_settings_window.account_mapping_tab.settings = temp_settings
    new_settings_window.super_group_mapping_tab.settings = temp_settings
    new_settings_window.load_settings()
    
    reloaded_mappings = len(new_settings_window.account_mapping_tab.account_mappings)
    reloaded_names = len(new_settings_window.account_mapping_tab.account_names)
    reloaded_super_groups = len(new_settings_window.super_group_mapping_tab.super_group_mappings)
    reloaded_list_count = new_settings_window.account_mapping_tab.accounts_list.count()
    
    print(f"   Nach Neustart - BWA-Mappings: {reloaded_mappings}")
    print(f"   Nach Neustart - Sachkonten-Namen: {reloaded_names}")
    print(f"   Nach Neustart - Obergruppen: {reloaded_super_groups}")
    print(f"   Nach Neustart - Listen-Einträge: {reloaded_list_count}")
    
    # Erfolg prüfen
    persistence_ok = (saved_mappings == reloaded_mappings and 
                      saved_names == reloaded_names and
                      saved_super_groups == reloaded_super_groups and
                      list_count == reloaded_list_count)
    
    if persistence_ok:
        print("\n✅ ECHTER CSV IMPORT UND PERSISTIERUNG ERFOLGREICH!")
        print("   - Sachkonten-Zuordnungen bleiben nach Neustart erhalten")
        print("   - BWA-Gruppen zu Obergruppen-Zuordnungen funktionieren")
        print("   - Listen werden korrekt befüllt")
    else:
        print("\n❌ PROBLEME BEI PERSISTIERUNG!")
        
    # Einige Beispiele anzeigen
    print("\n6. Beispiele aus den importierten Daten:")
    example_accounts = list(imported_mappings.items())[:5]
    for account, group in example_accounts:
        name = imported_names.get(account, "Unbekannt")
        super_group = imported_super_groups.get(group, "Keine Obergruppe")
        print(f"   {account}: {name} → {group} → {super_group}")
    
    # Aufräumen
    temp_settings.clear()
    
    print("\n=== Test abgeschlossen ===")

if __name__ == "__main__":
    test_real_bwa_csv()

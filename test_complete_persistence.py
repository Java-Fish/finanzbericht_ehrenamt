#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vollständiger Test für alle Persistierung-Features
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings, QRect
from src.main_window import MainWindow
from src.settings.settings_window import SettingsWindow

def test_complete_persistence():
    """Vollständiger Test aller Persistierung-Features"""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    print("=== Vollständiger Persistierung-Test ===")
    
    # Temporäre Settings verwenden
    temp_settings = QSettings("TestOrg", "CompletePersistenceTest")
    temp_settings.clear()  # Sauberer Start
    
    print("\n1. Hauptfenster - Kompletttest...")
    
    # Hauptfenster erstellen und konfigurieren
    main_window = MainWindow()
    main_window.settings = temp_settings
    
    # Geometrie setzen
    main_geometry = QRect(150, 150, 1100, 750)
    main_window.setGeometry(main_geometry)
    
    # Hauptfenster "schließen" (closeEvent simulieren)
    main_window.settings.setValue("geometry", main_window.saveGeometry())
    main_window.settings.sync()
    
    print("   ✅ Hauptfenster-Geometrie gespeichert")
    
    print("\n2. Einstellungsfenster - Kompletttest...")
    
    # Einstellungsfenster erstellen
    settings_window = SettingsWindow()
    settings_window.settings = temp_settings
    
    # Geometrie setzen
    settings_geometry = QRect(250, 250, 950, 700)
    settings_window.setGeometry(settings_geometry)
    
    # Test-Sachkonten hinzufügen
    test_account_mappings = {
        "1000": "Kasse",
        "4000": "Umsatzerlöse",
        "6000": "Löhne"
    }
    
    test_account_names = {
        "1000": "Kasse",
        "4000": "Umsatzerlöse", 
        "6000": "Löhne und Gehälter"
    }
    
    test_super_groups = {
        "Erträge": "Einnahmen",
        "Personalkosten": "Ausgaben"
    }
    
    # Daten in Account-Mapping setzen
    account_tab = settings_window.account_mapping_tab
    account_tab.settings = temp_settings
    account_tab.account_mappings.update(test_account_mappings)
    account_tab.account_names.update(test_account_names)
    account_tab.save_settings()
    
    # Obergruppen setzen
    super_tab = settings_window.super_group_mapping_tab
    super_tab.settings = temp_settings
    super_tab.super_group_mappings.update(test_super_groups)
    super_tab.save_settings()
    
    # Einstellungsfenster "schließen" (closeEvent simulieren)
    settings_window.settings.setValue("settings_window/geometry", settings_window.saveGeometry())
    settings_window.settings.sync()
    
    print("   ✅ Einstellungsfenster-Geometrie gespeichert")
    print("   ✅ Sachkonto-Mappings gespeichert")
    print("   ✅ Obergruppen-Mappings gespeichert")
    
    print("\n3. Neustart-Simulation - Alles laden...")
    
    # Neues Hauptfenster erstellen und laden
    new_main_window = MainWindow()
    new_main_window.settings = temp_settings
    new_main_window.load_settings()
    
    # Neues Einstellungsfenster erstellen und laden
    new_settings_window = SettingsWindow()
    new_settings_window.settings = temp_settings
    new_settings_window.load_settings()
    
    print("\n4. Verifikation...")
    
    # Hauptfenster-Geometrie prüfen
    loaded_main_geometry = new_main_window.geometry()
    main_geometry_ok = (loaded_main_geometry.width() == main_geometry.width() and 
                       loaded_main_geometry.height() == main_geometry.height())
    
    # Einstellungsfenster-Geometrie prüfen
    loaded_settings_geometry = new_settings_window.geometry()
    settings_geometry_ok = (loaded_settings_geometry.width() == settings_geometry.width() and 
                           loaded_settings_geometry.height() == settings_geometry.height())
    
    # Account-Mappings prüfen
    new_account_tab = new_settings_window.account_mapping_tab
    new_account_tab.settings = temp_settings  # Settings explizit setzen
    new_account_tab.load_settings()  # Explizit laden
    
    loaded_account_mappings = new_account_tab.account_mappings
    loaded_account_names = new_account_tab.account_names
    account_mappings_ok = loaded_account_mappings == test_account_mappings
    account_names_ok = loaded_account_names == test_account_names
    
    # Obergruppen-Mappings prüfen
    new_super_tab = new_settings_window.super_group_mapping_tab
    new_super_tab.settings = temp_settings  # Settings explizit setzen
    new_super_tab.load_settings()  # Explizit laden
    
    loaded_super_groups = new_super_tab.super_group_mappings
    super_groups_ok = all(group in loaded_super_groups for group in test_super_groups)
    
    # Liste-Population prüfen
    accounts_list_count = new_account_tab.accounts_list.count()
    list_populated = accounts_list_count == len(test_account_mappings)
    
    print(f"   Hauptfenster-Geometrie: {'✅' if main_geometry_ok else '❌'}")
    print(f"   Einstellungen-Geometrie: {'✅' if settings_geometry_ok else '❌'}")
    print(f"   Sachkonto-Mappings: {'✅' if account_mappings_ok else '❌'} ({len(loaded_account_mappings)}/{len(test_account_mappings)})")
    print(f"   Sachkonto-Namen: {'✅' if account_names_ok else '❌'} ({len(loaded_account_names)}/{len(test_account_names)})")
    print(f"   Obergruppen: {'✅' if super_groups_ok else '❌'} ({len([g for g in test_super_groups if g in loaded_super_groups])}/{len(test_super_groups)})")
    print(f"   Liste befüllt: {'✅' if list_populated else '❌'} ({accounts_list_count} Einträge)")
    
    # Gesamtergebnis
    all_features_ok = (main_geometry_ok and settings_geometry_ok and 
                      account_mappings_ok and account_names_ok and 
                      super_groups_ok and list_populated)
    
    print("\n5. Gesamtergebnis...")
    
    if all_features_ok:
        print("✅ ALLE PERSISTIERUNG-FEATURES FUNKTIONIEREN!")
        print("   🪟 Fenstergrößen werden gespeichert und geladen")
        print("   📊 Sachkonto-Zuordnungen bleiben erhalten")
        print("   📁 Obergruppen-Zuordnungen bleiben erhalten")
        print("   📋 Listen werden beim Start befüllt")
        print("   🔄 Neustart behält alle Einstellungen")
    else:
        print("❌ EINIGE PERSISTIERUNG-FEATURES FEHLERHAFT!")
        
    # Aufräumen
    temp_settings.clear()
    
    print("\n=== Kompletttest abgeschlossen ===")

if __name__ == "__main__":
    test_complete_persistence()

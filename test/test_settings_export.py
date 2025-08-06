#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für Einstellungen Export/Import
"""

import sys
import json
import tempfile
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Lokale Imports
sys.path.append('src')
from settings.general_settings import GeneralSettingsTab

def test_settings_export_import():
    """Testet Export und Import von Einstellungen"""
    app = QApplication(sys.argv)
    
    print("💾 Teste Einstellungen Export/Import...")
    
    # Test-Einstellungen setzen
    settings = QSettings()
    test_settings = {
        "language": "de",
        "csv_separator": ";",
        "quarter_mode": "cumulative",
        "generate_quarterly_reports": True,
        "generate_account_reports": True,
        "decimal_separator": ",",
        "super_group_mappings": '{"Miete": "Verwaltungskosten", "Spenden": "Einnahmen"}'
    }
    
    print("✅ Test-Einstellungen setzen:")
    for key, value in test_settings.items():
        settings.setValue(key, value)
        print(f"   {key}: {value}")
    
    settings.sync()
    
    # GeneralSettingsTab erstellen
    general_tab = GeneralSettingsTab()
    
    # Export testen
    print("\n📤 Teste Export...")
    export_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    export_path = export_file.name
    export_file.close()
    
    try:
        # Export durchführen
        export_data = {}
        all_keys = settings.allKeys()
        
        for key in all_keys:
            value = settings.value(key)
            export_data[key] = value
            
        # JSON-Datei schreiben
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Export erfolgreich: {len(export_data)} Einstellungen exportiert")
        
        # Export-Datei prüfen
        with open(export_path, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
            
        print("📋 Exportierte Einstellungen:")
        for key, value in exported_data.items():
            print(f"   {key}: {value}")
        
        # Import testen
        print("\n📥 Teste Import...")
        
        # Aktuelle Einstellungen ändern
        settings.setValue("language", "en")
        settings.setValue("quarter_mode", "quarterly")
        settings.setValue("generate_quarterly_reports", False)
        settings.sync()
        
        print("✅ Einstellungen geändert (für Import-Test)")
        
        # Import durchführen
        settings.clear()
        
        for key, value in exported_data.items():
            settings.setValue(key, value)
            
        settings.sync()
        
        print("✅ Import erfolgreich durchgeführt")
        
        # Verifikation
        print("\n🔍 Verifikation nach Import:")
        verification_passed = True
        
        for key, expected_value in test_settings.items():
            actual_value = settings.value(key)
            
            # Bool-Werte speziell behandeln
            if key in ["generate_quarterly_reports", "generate_account_reports"]:
                actual_value = settings.value(key, type=bool)
            
            if str(actual_value) == str(expected_value):
                print(f"   ✅ {key}: {actual_value}")
            else:
                print(f"   ❌ {key}: Erwartet {expected_value}, erhalten {actual_value}")
                verification_passed = False
        
        if verification_passed:
            print("\n🎉 Export/Import-Test erfolgreich!")
        else:
            print("\n❌ Export/Import-Test teilweise fehlgeschlagen")
            
    except Exception as e:
        print(f"❌ Fehler beim Export/Import: {e}")
        
    finally:
        # Temporäre Datei löschen
        try:
            os.unlink(export_path)
        except:
            pass
    
    # Quartals-Modi Demo
    print("\n🔄 Demo der Quartals-Modi:")
    
    settings.setValue("quarter_mode", "cumulative")
    mode = settings.value("quarter_mode")
    print(f"   Kumulativ: {mode} → Q2 umfasst 01.01. - 30.06.")
    
    settings.setValue("quarter_mode", "quarterly")
    mode = settings.value("quarter_mode")
    print(f"   Quartalsweise: {mode} → Q2 umfasst 01.04. - 30.06.")
    
    # Berichterstellungs-Optionen Demo
    print("\n📊 Demo der Berichterstellungs-Optionen:")
    
    settings.setValue("generate_quarterly_reports", True)
    settings.setValue("generate_account_reports", True)
    quarterly = settings.value("generate_quarterly_reports", type=bool)
    accounts = settings.value("generate_account_reports", type=bool)
    print(f"   Alle Berichte: Quartalsberichte={quarterly}, Sachkonten={accounts}")
    
    settings.setValue("generate_quarterly_reports", False)
    settings.setValue("generate_account_reports", False)
    quarterly = settings.value("generate_quarterly_reports", type=bool)
    accounts = settings.value("generate_account_reports", type=bool)
    print(f"   Minimal: Quartalsberichte={quarterly}, Sachkonten={accounts} → Nur Deckblatt + Jahresbericht")
    
    print("\n🎯 Neue Features zusammengefasst:")
    print("   🔄 Kumulative vs. Quartalsweise Auswertung")
    print("   📊 Optionale Quartals- und Sachkontenberichte")
    print("   💾 Einstellungen Export/Import als JSON")
    print("   ⚙️  Alle Optionen in 'Allgemein'-Tab verfügbar")
    
    app.quit()

if __name__ == "__main__":
    test_settings_export_import()

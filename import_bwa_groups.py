#!/usr/bin/env python3
"""
Script zum Importieren der BWA-Gruppen aus CSV in die Anwendungseinstellungen
"""

import os
import sys
import csv
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

def import_bwa_groups_to_settings():
    """Importiert BWA-Gruppen aus CSV in die Anwendungseinstellungen"""
    print("📥 Importiere BWA-Gruppen aus CSV in Anwendungseinstellungen...")
    
    csv_export_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/bwa_gruppen_export.csv"
    
    if not os.path.exists(csv_export_path):
        print(f"❌ BWA-Gruppen Export-CSV nicht gefunden: {csv_export_path}")
        return False
    
    # QApplication für QSettings
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    try:
        # 1. BWA-Gruppen und Account-Namen aus CSV laden
        account_mappings = {}
        account_names = {}
        
        with open(csv_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                sachkontonr = str(row.get('Sachkontonr.', '')).strip()
                sachkonto = row.get('Sachkonto', '').strip()
                bwa_gruppe = row.get('BWA-Gruppe', '').strip()
                
                if sachkontonr:
                    if sachkonto:
                        account_names[sachkontonr] = sachkonto
                    if bwa_gruppe:
                        account_mappings[sachkontonr] = bwa_gruppe
        
        print(f"✅ Aus CSV gelesen: {len(account_mappings)} BWA-Mappings, {len(account_names)} Account-Namen")
        
        # 2. In QSettings speichern (wie die AccountMappingTab es macht)
        settings = QSettings()
        
        # Account-Mappings speichern
        for account, bwa_group in account_mappings.items():
            settings.setValue(f"account_mapping/{account}", bwa_group)
        
        # Account-Namen speichern
        for account, name in account_names.items():
            settings.setValue(f"account_names/{account}", name)
        
        print(f"✅ In QSettings gespeichert:")
        print(f"  - {len(account_mappings)} BWA-Mappings")
        print(f"  - {len(account_names)} Account-Namen")
        
        # 3. Validierung: Einstellungen wieder lesen
        print(f"\n🔍 Validierung:")
        loaded_mappings = {}
        loaded_names = {}
        
        # Alle account_mapping Keys lesen
        settings.beginGroup("account_mapping")
        for key in settings.allKeys():
            loaded_mappings[key] = settings.value(key, "")
        settings.endGroup()
        
        # Alle account_names Keys lesen
        settings.beginGroup("account_names")
        for key in settings.allKeys():
            loaded_names[key] = settings.value(key, "")
        settings.endGroup()
        
        print(f"Geladene Mappings: {len(loaded_mappings)}")
        print(f"Geladene Namen: {len(loaded_names)}")
        
        # Stichproben
        print(f"\n📋 Stichproben der gespeicherten Daten:")
        count = 0
        for account, bwa_group in sorted(account_mappings.items()):
            if count < 10:
                name = account_names.get(account, "")
                loaded_group = loaded_mappings.get(account, "")
                loaded_name = loaded_names.get(account, "")
                
                success_marker = "✅" if (loaded_group == bwa_group and loaded_name == name) else "❌"
                print(f"  {success_marker} {account}: {name} → {bwa_group}")
                count += 1
        
        # Überprüfung der Konsistenz
        mappings_ok = loaded_mappings == account_mappings
        names_ok = loaded_names == account_names
        
        if mappings_ok and names_ok:
            print(f"\n✅ Alle Daten korrekt in QSettings gespeichert!")
            return True
        else:
            print(f"\n❌ Daten-Inkonsistenz:")
            print(f"  Mappings OK: {mappings_ok}")
            print(f"  Namen OK: {names_ok}")
            return False
        
    except Exception as e:
        print(f"❌ Fehler beim Import: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_settings_integration():
    """Überprüft die Integration mit den Anwendungseinstellungen"""
    print(f"\n🧪 Teste Integration mit Anwendungseinstellungen...")
    
    # QApplication für QSettings
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    try:
        # Simuliere, was AccountMappingTab.get_account_mappings() macht
        settings = QSettings()
        account_mappings = {}
        
        settings.beginGroup("account_mapping")
        for key in settings.allKeys():
            value = settings.value(key, "")
            if value:  # Nur nicht-leere Werte
                account_mappings[key] = value
        settings.endGroup()
        
        print(f"📊 Über get_account_mappings() verfügbar: {len(account_mappings)} Mappings")
        
        if account_mappings:
            # Zeige BWA-Gruppen-Verteilung
            bwa_groups = {}
            for account, group in account_mappings.items():
                if group not in bwa_groups:
                    bwa_groups[group] = 0
                bwa_groups[group] += 1
            
            print(f"\n📈 BWA-Gruppen-Verteilung:")
            for group, count in sorted(bwa_groups.items()):
                print(f"  {group}: {count} Sachkonten")
            
            return True
        else:
            print(f"❌ Keine Account-Mappings gefunden!")
            return False
        
    except Exception as e:
        print(f"❌ Fehler bei der Integration-Verifikation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("📥 BWA-Gruppen CSV Import in Anwendungseinstellungen")
    print("=" * 60)
    
    # Import der BWA-Gruppen
    import_success = import_bwa_groups_to_settings()
    
    if import_success:
        # Verifikation der Integration
        verify_success = verify_settings_integration()
        
        overall_success = import_success and verify_success
        print(f"\n{'🎉 BWA-Gruppen erfolgreich in Anwendung importiert!' if overall_success else '💥 Fehler beim Import oder Verifikation!'}")
        
        if overall_success:
            print(f"\n📋 Nächste Schritte:")
            print(f"1. Starte die Anwendung (python main.py)")
            print(f"2. Lade eine CSV-Datei")
            print(f"3. Erstelle eine BWA - alle BWA-Gruppen sollten nun korrekt angezeigt werden")
            print(f"4. Die Kategorien sollten dem angehängten PDF entsprechen")
    else:
        print(f"\n💥 Fehler beim Import der BWA-Gruppen!")
    
    sys.exit(0 if import_success else 1)

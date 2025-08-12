#!/usr/bin/env python3
"""
Script zum Aktualisieren der Super-Group-Mappings basierend auf BWA-Gruppen CSV
"""

import os
import sys
import csv
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

def update_super_group_mappings():
    """Aktualisiert die Super-Group-Mappings basierend auf der BWA-Gruppen CSV"""
    print("🔧 Aktualisiere Super-Group-Mappings...")
    
    csv_export_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/bwa_gruppen_export.csv"
    
    if not os.path.exists(csv_export_path):
        print(f"❌ BWA-Gruppen Export-CSV nicht gefunden: {csv_export_path}")
        return False
    
    # QApplication für QSettings
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    try:
        # 1. BWA-Gruppen aus CSV sammeln
        bwa_groups = set()
        
        with open(csv_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                bwa_gruppe = row.get('BWA-Gruppe', '').strip()
                if bwa_gruppe:
                    bwa_groups.add(bwa_gruppe)
        
        print(f"📊 Gefundene BWA-Gruppen: {len(bwa_groups)}")
        for group in sorted(bwa_groups):
            print(f"  - {group}")
        
        # 2. Korrekte Super-Group-Mappings definieren
        # Basierend auf dem PDF-Screenshot und den BWA-Standardkategorien
        correct_super_group_mappings = {
            # Einnahmen aus ideellem Bereich
            "Förderung": "Einnahmen aus ideellem Bereich",
            "Sonstige Einnahmen": "Einnahmen aus ideellem Bereich", 
            "Spenden": "Einnahmen aus ideellem Bereich",
            
            # Kosten ideeller Bereich
            "Bürokosten": "Kosten ideeller Bereich",
            "Gehalts- / Honorar- / Pauschalzahlung": "Kosten ideeller Bereich",
            "Sonstige Kosten ideeller Bereich": "Kosten ideeller Bereich",
            "Untergliederungen": "Kosten ideeller Bereich",
            "Projekte": "Kosten ideeller Bereich",
            
            # Vermögensverwaltung
            "Kosten Finanzanlagen": "Vermögensverwaltung"
        }
        
        print(f"\n📋 Neue Super-Group-Mappings:")
        for bwa_group, super_group in correct_super_group_mappings.items():
            print(f"  {bwa_group} → {super_group}")
        
        # 3. Prüfe ob alle BWA-Gruppen aus CSV abgedeckt sind
        missing_groups = bwa_groups - set(correct_super_group_mappings.keys())
        if missing_groups:
            print(f"\n⚠️  BWA-Gruppen ohne Super-Group-Zuordnung:")
            for group in sorted(missing_groups):
                print(f"  - {group}")
            
            # Automatisch zu "Kosten ideeller Bereich" zuordnen
            for group in missing_groups:
                correct_super_group_mappings[group] = "Kosten ideeller Bereich"
                print(f"  Auto-Zuordnung: {group} → Kosten ideeller Bereich")
        
        # 4. Super-Group-Mappings in QSettings speichern
        settings = QSettings()
        mappings_json = json.dumps(correct_super_group_mappings, ensure_ascii=False, indent=2)
        settings.setValue("super_group_mappings", mappings_json)
        
        print(f"\n✅ Super-Group-Mappings aktualisiert!")
        print(f"📊 Gespeichert: {len(correct_super_group_mappings)} Zuordnungen")
        
        # 5. Validierung: Mappings wieder lesen
        loaded_mappings_json = settings.value("super_group_mappings", "{}")
        loaded_mappings = json.loads(loaded_mappings_json)
        
        print(f"\n🔍 Validierung:")
        print(f"Gespeicherte Mappings: {len(loaded_mappings)}")
        if loaded_mappings == correct_super_group_mappings:
            print("✅ Mappings korrekt gespeichert!")
        else:
            print("❌ Mappings stimmen nicht überein!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Aktualisieren: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_updated_mappings():
    """Testet die aktualisierten Mappings mit BWA-PDF-Generierung"""
    print("\n🧪 Teste aktualisierte Mappings...")
    
    # Test mit dem vorherigen Test-Script
    import subprocess
    
    try:
        result = subprocess.run([
            sys.executable, 
            "/Users/nabu/git/finanzauswertungEhrenamt/test_bwa_groups_csv.py"
        ], capture_output=True, text=True, cwd="/Users/nabu/git/finanzauswertungEhrenamt")
        
        print("📊 Test-Ausgabe:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Fehler:")
            print(result.stderr)
        
        success = result.returncode == 0
        if success:
            print("✅ Test mit aktualisierten Mappings erfolgreich!")
        else:
            print("❌ Test mit aktualisierten Mappings fehlgeschlagen!")
        
        return success
        
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Super-Group-Mappings Update")
    print("=" * 50)
    
    # Update der Mappings
    update_success = update_super_group_mappings()
    
    if update_success:
        # Test mit aktualisierten Mappings
        test_success = test_updated_mappings()
        
        overall_success = update_success and test_success
        print(f"\n{'🎉 Mappings erfolgreich aktualisiert und getestet!' if overall_success else '💥 Fehler beim Update oder Test!'}")
    else:
        print("\n💥 Fehler beim Update der Mappings!")
    
    sys.exit(0 if update_success else 1)

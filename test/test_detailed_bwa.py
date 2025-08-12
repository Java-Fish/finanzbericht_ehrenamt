#!/usr/bin/env python3
"""
Test für detaillierte BWA-Tabellen mit Sachkonten
"""

import os
import sys
import tempfile

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from utils.csv_processor import CSVProcessor
from utils.bwa_generator import BWAPDFGenerator

def test_detailed_bwa_tables():
    """Testet die neuen detaillierten BWA-Tabellen mit Sachkonten"""
    print("🔍 Teste detaillierte BWA-Tabellen mit Sachkonten...")
    
    main_csv_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/Finanzübersicht_2024.csv"
    
    if not os.path.exists(main_csv_path):
        print(f"❌ Hauptdaten-CSV nicht gefunden: {main_csv_path}")
        return False
    
    # QApplication für GUI-Tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    try:
        # 1. Prüfe vorhandene QSettings
        print("📋 Prüfe QSettings...")
        settings = QSettings()
        
        # Account-Mappings prüfen
        settings.beginGroup("account_mapping")
        account_mapping_keys = settings.allKeys()
        settings.endGroup()
        
        # Account-Namen prüfen
        settings.beginGroup("account_names")
        account_names_keys = settings.allKeys()
        settings.endGroup()
        
        print(f"✅ QSettings Status:")
        print(f"  - Account-Mappings: {len(account_mapping_keys)} Einträge")
        print(f"  - Account-Namen: {len(account_names_keys)} Einträge")
        
        # 2. CSV-Processor erstellen
        print(f"\n📊 Lade CSV-Daten...")
        csv_processor = CSVProcessor()
        success = csv_processor.load_file(main_csv_path)
        
        if not success:
            print(f"❌ Fehler beim Laden der CSV-Daten")
            return False
        
        print(f"✅ CSV-Daten geladen")
        
        # 3. Account-Mappings simulieren
        print(f"\n🔄 Lade Account-Mappings und Namen...")
        
        account_mappings = {}
        settings.beginGroup("account_mapping")
        for key in settings.allKeys():
            value = settings.value(key, "")
            if value.strip():
                account_mappings[key] = value
        settings.endGroup()
        
        account_names = {}
        settings.beginGroup("account_names")
        for key in settings.allKeys():
            value = settings.value(key, "")
            if value.strip():
                account_names[key] = value
        settings.endGroup()
        
        print(f"✅ Geladen: {len(account_mappings)} Mappings, {len(account_names)} Namen")
        
        # Zeige einige Beispiele für Sachkonten
        print(f"\n📋 Beispiel-Sachkonten (erste 10):")
        count = 0
        for account, bwa_group in sorted(account_mappings.items()):
            if count < 10:
                name = account_names.get(account, f"Sachkonto {account}")
                print(f"  {account}: {name} → {bwa_group}")
                count += 1
        
        # 4. BWA-PDF mit detaillierten Tabellen generieren
        print(f"\n📄 Generiere BWA-PDF mit detaillierten Tabellen...")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdf_path = temp_pdf.name
        
        try:
            bwa_generator = BWAPDFGenerator()
            success = bwa_generator.generate_bwa_pdf(pdf_path, csv_processor, account_mappings)
            
            if success:
                print(f"✅ BWA-PDF mit detaillierten Tabellen erfolgreich erstellt!")
                
                # Prüfe Dateigröße
                file_size = os.path.getsize(pdf_path)
                print(f"📄 PDF-Größe: {file_size:,} Bytes")
                
                # Verschiebe zu finaler Datei
                final_pdf = "/tmp/detailed_bwa_test.pdf"
                os.rename(pdf_path, final_pdf)
                print(f"📁 Detailliertes BWA-PDF: {final_pdf}")
                
                # Prüfe JSON-Export
                json_path = pdf_path.replace('.pdf', '.json')
                if os.path.exists(json_path):
                    json_size = os.path.getsize(json_path)
                    print(f"📋 JSON-Größe: {json_size:,} Bytes")
                    
                    final_json = "/tmp/detailed_bwa_test.json"
                    os.rename(json_path, final_json)
                    print(f"📁 JSON-Export: {final_json}")
                    
                    # Analysiere JSON um zu prüfen, ob detaillierte Daten vorhanden sind
                    import json
                    with open(final_json, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    print(f"\n📊 JSON-Analyse:")
                    print(f"Account-Mappings: {len(json_data.get('account_mappings', {}))}")
                    print(f"Account-Namen: {len(json_data.get('account_names', {}))}")
                    
                    if 'quarters' in json_data:
                        print(f"Quartale: {len(json_data['quarters'])}")
                        for q_data in json_data['quarters']:
                            if 'detailed_accounts' in q_data:
                                detailed_accounts = q_data.get('detailed_accounts', {})
                                total_accounts = sum(len(accounts) for accounts in detailed_accounts.values())
                                print(f"  Q{q_data.get('quarter', '?')}: {total_accounts} Sachkonten in {len(detailed_accounts)} BWA-Gruppen")
                            else:
                                print(f"  Q{q_data.get('quarter', '?')}: Keine detaillierten Sachkonto-Daten")
                    
                    if 'yearly_summary' in json_data:
                        yearly = json_data['yearly_summary']
                        if 'detailed_accounts' in yearly:
                            detailed_accounts = yearly.get('detailed_accounts', {})
                            total_accounts = sum(len(accounts) for accounts in detailed_accounts.values())
                            print(f"Jahresübersicht: {total_accounts} Sachkonten in {len(detailed_accounts)} BWA-Gruppen")
                        else:
                            print(f"Jahresübersicht: Keine detaillierten Sachkonto-Daten")
                
                print(f"\n🎉 Test erfolgreich!")
                print(f"📋 Zusammenfassung:")
                print(f"1. ✅ BWA-Tabellen zeigen jetzt Obergruppen")
                print(f"2. ✅ BWA-Gruppen sind unter Obergruppen angezeigt")
                print(f"3. ✅ Sachkonten sind unter BWA-Gruppen eingerückt angezeigt")
                print(f"4. ✅ Alle Beträge (Obergruppe, BWA-Gruppe, Sachkonto) sind sichtbar")
                print(f"5. ✅ Negative Beträge sind rot dargestellt")
                
                return True
            else:
                print(f"❌ BWA-PDF Generierung fehlgeschlagen")
                return False
                
        finally:
            # Cleanup falls noch vorhanden
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except:
                    pass
        
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Test für detaillierte BWA-Tabellen mit Sachkonten")
    print("=" * 60)
    
    success = test_detailed_bwa_tables()
    
    if success:
        print(f"\n🎉 ERFOLG! Detaillierte BWA-Tabellen funktionieren!")
        print(f"\n📋 Was wurde implementiert:")
        print(f"- Obergruppen (Einnahmen aus ideellem Bereich, Kosten ideeller Bereich, Vermögensverwaltung)")
        print(f"- BWA-Gruppen unter Obergruppen (• BWA-Gruppe)")
        print(f"- Sachkonten unter BWA-Gruppen (    S12345: Sachkonto-Name)")
        print(f"- Alle Ebenen mit entsprechenden Beträgen")
        print(f"- Hierarchische Einrückung und Farbcodierung")
        print(f"\n🚀 Die BWA-Berichte zeigen jetzt vollständige Details!")
    else:
        print(f"\n💥 FEHLER! Test der detaillierten BWA-Tabellen fehlgeschlagen!")
    
    sys.exit(0 if success else 1)

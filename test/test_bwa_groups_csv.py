#!/usr/bin/env python3
"""
Test-Script für BWA-Gruppen aus CSV-Export in PDF-Generierung
"""

import os
import sys
import csv
import tempfile
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from settings.account_mapping import AccountMappingTab
from utils.csv_processor import CSVProcessor
from utils.bwa_generator import BWAPDFGenerator

def test_bwa_groups_from_csv():
    """Testet BWA-Gruppenzuordnung aus CSV-Export"""
    print("🧪 Teste BWA-Gruppen aus CSV-Export...")
    
    csv_export_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/bwa_gruppen_export.csv"
    main_csv_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/Finanzübersicht_2024.csv"
    
    if not os.path.exists(csv_export_path):
        print(f"❌ BWA-Gruppen Export-CSV nicht gefunden: {csv_export_path}")
        return False
        
    if not os.path.exists(main_csv_path):
        print(f"❌ Hauptdaten-CSV nicht gefunden: {main_csv_path}")
        return False
    
    # QApplication für GUI-Tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    try:
        # 1. BWA-Gruppen aus Export-CSV laden
        print("📥 Lade BWA-Gruppen aus Export-CSV...")
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
        
        print(f"✅ Geladen: {len(account_mappings)} BWA-Mappings, {len(account_names)} Account-Namen")
        
        # Zeige einige Beispiele
        print("\n📋 Beispiel-Mappings aus CSV:")
        count = 0
        for acc, group in sorted(account_mappings.items()):
            if count < 10:
                name = account_names.get(acc, "")
                print(f"  {acc}: {name} → {group}")
                count += 1
        
        # 2. CSV-Processor für Hauptdaten erstellen
        print("\n📊 Lade Hauptdaten...")
        csv_processor = CSVProcessor()
        success = csv_processor.load_file(main_csv_path)
        
        if not success:
            print(f"❌ Fehler beim Laden der Hauptdaten: {main_csv_path}")
            return False
        
        # Berichte verfügbare Sachkonten
        if hasattr(csv_processor, 'data') and csv_processor.data is not None:
            available_accounts = set(str(acc) for acc in csv_processor.data['Sachkontonr.'].unique() if str(acc) != 'nan')
            print(f"✅ Verfügbare Sachkonten in Daten: {len(available_accounts)}")
            
            # Übereinstimmung prüfen
            mapped_accounts = set(account_mappings.keys())
            overlap = available_accounts & mapped_accounts
            print(f"📈 Übereinstimmung: {len(overlap)} von {len(available_accounts)} Sachkonten haben BWA-Mappings")
            
            # Zeige Konten ohne Mapping
            unmapped = available_accounts - mapped_accounts
            if unmapped:
                print(f"⚠️  Sachkonten ohne BWA-Mapping: {len(unmapped)}")
                if len(unmapped) <= 10:
                    print(f"   {', '.join(sorted(unmapped))}")
                else:
                    print(f"   {', '.join(list(sorted(unmapped))[:10])}... (und {len(unmapped)-10} weitere)")
        
        # 3. BWA-PDF generieren mit Mappings
        print("\n🔄 Generiere BWA-PDF mit Mappings...")
        
        # Temporäres PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdf_path = temp_pdf.name
        
        try:
            bwa_generator = BWAPDFGenerator()
            success = bwa_generator.generate_bwa_pdf(pdf_path, csv_processor, account_mappings)
            
            if success:
                print(f"✅ BWA-PDF erfolgreich erstellt: {pdf_path}")
                
                # Prüfe ob JSON-Export ebenfalls erstellt wurde
                json_path = pdf_path.replace('.pdf', '.json')
                if os.path.exists(json_path):
                    print(f"✅ JSON-Export ebenfalls erstellt: {json_path}")
                    
                    # JSON-Inhalt analysieren
                    import json
                    with open(json_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    # Prüfe account_mappings im JSON
                    if 'account_mappings' in json_data:
                        json_mappings = json_data['account_mappings']
                        print(f"📊 JSON enthält {len(json_mappings)} Account-Mappings")
                        
                        # Vergleiche mit ursprünglichen Mappings
                        if json_mappings == account_mappings:
                            print("✅ JSON Account-Mappings stimmen überein")
                        else:
                            print("⚠️  JSON Account-Mappings weichen ab")
                    
                    # Prüfe Quartalsberichte
                    if 'quarters' in json_data:
                        quarters = json_data['quarters']
                        print(f"📈 JSON enthält {len(quarters)} Quartalsberichte")
                        
                        for quarter_data in quarters:
                            if 'summary' in quarter_data:
                                summary = quarter_data['summary']
                                print(f"   Q{quarter_data.get('quarter', '?')}: {len(summary)} Obergruppen")
                                
                                # Zähle BWA-Gruppen
                                bwa_group_count = 0
                                for obergruppe, bwa_groups in summary.items():
                                    bwa_group_count += len(bwa_groups)
                                
                                print(f"      {bwa_group_count} BWA-Gruppen total")
                
                return True
            else:
                print("❌ BWA-PDF Generierung fehlgeschlagen")
                return False
                
        finally:
            # Cleanup
            if os.path.exists(pdf_path):
                # PDF für Inspektion behalten
                final_pdf = "/tmp/test_bwa_with_groups.pdf"
                os.rename(pdf_path, final_pdf)
                print(f"📄 Test-PDF verfügbar unter: {final_pdf}")
            
            json_path = pdf_path.replace('.pdf', '.json')
            if os.path.exists(json_path):
                final_json = "/tmp/test_bwa_with_groups.json"
                os.rename(json_path, final_json)
                print(f"📋 Test-JSON verfügbar unter: {final_json}")
        
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_bwa_groups():
    """Vergleicht BWA-Gruppen zwischen CSV-Export und dem angehängten PDF"""
    print("\n🔍 Vergleiche BWA-Gruppen...")
    
    csv_export_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/bwa_gruppen_export.csv"
    
    if not os.path.exists(csv_export_path):
        print(f"❌ BWA-Gruppen Export-CSV nicht gefunden: {csv_export_path}")
        return False
    
    try:
        # Gruppen aus CSV sammeln
        csv_groups = set()
        csv_mappings = {}
        
        with open(csv_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                sachkontonr = str(row.get('Sachkontonr.', '')).strip()
                bwa_gruppe = row.get('BWA-Gruppe', '').strip()
                
                if bwa_gruppe:
                    csv_groups.add(bwa_gruppe)
                    csv_mappings[sachkontonr] = bwa_gruppe
        
        print(f"📊 CSV enthält {len(csv_groups)} einzigartige BWA-Gruppen:")
        for group in sorted(csv_groups):
            count = sum(1 for g in csv_mappings.values() if g == group)
            print(f"   {group}: {count} Sachkonten")
        
        # Gruppen aus angehängtem PDF analysieren
        pdf_groups_expected = {
            "Einnahmen aus ideellem Bereich": [
                "Förderung", "Sonstige Einnahmen", "Spenden"
            ],
            "Kosten ideeller Bereich": [
                "Bürokosten", "Gehalts- / Honorar- / Pauschalzahlung", 
                "Sonstige Kosten ideeller Bereich", "Untergliederungen", "Projekte"
            ],
            "Vermögensverwaltung": [
                "Kosten Finanzanlagen"
            ]
        }
        
        print(f"\n📋 PDF sollte folgende Struktur haben:")
        for obergruppe, bwa_groups in pdf_groups_expected.items():
            print(f"   {obergruppe}:")
            for bwa_group in bwa_groups:
                if bwa_group in csv_groups:
                    count = sum(1 for g in csv_mappings.values() if g == bwa_group)
                    print(f"     ✅ {bwa_group}: {count} Sachkonten")
                else:
                    print(f"     ❌ {bwa_group}: nicht in CSV gefunden")
        
        # Prüfe unzugeordnete Gruppen
        expected_flat = set()
        for groups in pdf_groups_expected.values():
            expected_flat.update(groups)
        
        unexpected = csv_groups - expected_flat
        if unexpected:
            print(f"\n⚠️  Unerwartete BWA-Gruppen in CSV (evtl. neue/andere Zuordnung):")
            for group in sorted(unexpected):
                count = sum(1 for g in csv_mappings.values() if g == group)
                print(f"   {group}: {count} Sachkonten")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Vergleich: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 BWA-Gruppen CSV-Export zu PDF Test")
    print("=" * 50)
    
    # Test 1: Vergleiche BWA-Gruppen
    test1_success = compare_bwa_groups()
    
    # Test 2: Teste PDF-Generierung mit CSV-Mappings
    test2_success = test_bwa_groups_from_csv()
    
    # Ergebnis
    overall_success = test1_success and test2_success
    print(f"\n{'🎉 BWA-Gruppen Tests erfolgreich!' if overall_success else '💥 Einige Tests fehlgeschlagen!'}")
    
    if overall_success:
        print("\n📋 Nächste Schritte:")
        print("1. Prüfe die generierten Test-Dateien in /tmp/")
        print("2. Importiere die BWA-Gruppen aus der CSV in die Anwendung")
        print("3. Teste die PDF-Generierung über die GUI")
    
    sys.exit(0 if overall_success else 1)

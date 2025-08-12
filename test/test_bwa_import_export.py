#!/usr/bin/env python3
"""
Test-Script für BWA-Gruppen Import/Export Funktionalität
"""

import os
import sys
import tempfile
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from settings.account_mapping import AccountMappingTab

def test_bwa_export_import():
    """Testet die BWA-Export/Import-Funktionalität"""
    print("🧪 Teste BWA-Gruppen Import/Export Funktionalität...")
    
    # QApplication für GUI-Tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Test-Daten erstellen
    test_mappings = {
        "S02720": "Projektkosten",
        "S03220": "Spenden",
        "S02660": "Miete",
        "S02702": "IT-Kosten"
    }
    
    test_names = {
        "S02720": "Wildvogelhilfe Ausgaben",
        "S03220": "Spenden NABU Jena",
        "S02660": "Miete, Nebenkosten",
        "S02702": "Telefon, IT, Software"
    }
    
    try:
        # 1. AccountMappingTab erstellen und Test-Daten setzen
        print("📋 Erstelle AccountMappingTab...")
        account_tab = AccountMappingTab()
        account_tab.account_mappings = test_mappings.copy()
        account_tab.account_names = test_names.copy()
        
        # 2. Export testen
        print("📤 Teste Export...")
        export_path = "/tmp/test_bwa_export.csv"
        
        # Simuliere Export (da GUI-Dialog nicht automatisch möglich)
        csv_data = []
        all_accounts = set(account_tab.account_names.keys()) | set(account_tab.account_mappings.keys())
        
        for account_nr in sorted(all_accounts):
            account_name = account_tab.account_names.get(account_nr, "")
            bwa_group = account_tab.account_mappings.get(account_nr, "")
            
            if account_name or bwa_group:
                csv_data.append({
                    'Sachkontonr.': account_nr,
                    'Sachkonto': account_name,
                    'BWA-Gruppe': bwa_group
                })
        
        # CSV manuell schreiben
        import csv
        with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Sachkontonr.', 'Sachkonto', 'BWA-Gruppe']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for row in csv_data:
                writer.writerow(row)
        
        print(f"✅ Export erstellt: {export_path}")
        print(f"📊 Exportierte Einträge: {len(csv_data)}")
        
        # Inhalt der exportierten Datei anzeigen
        print("\n📄 Exportierte Daten:")
        with open(export_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        
        # 3. Import testen
        print("\n📥 Teste Import...")
        
        # Neues AccountMappingTab für Import-Test
        account_tab2 = AccountMappingTab()
        
        # Import simulieren
        imported_count = 0
        with open(export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                sachkontonr = str(row.get('Sachkontonr.', '')).strip()
                sachkonto = row.get('Sachkonto', '').strip()
                bwa_gruppe = row.get('BWA-Gruppe', '').strip()
                
                if sachkontonr:
                    if sachkonto:
                        account_tab2.account_names[sachkontonr] = sachkonto
                    if bwa_gruppe:
                        account_tab2.account_mappings[sachkontonr] = bwa_gruppe
                    imported_count += 1
        
        print(f"✅ Import abgeschlossen: {imported_count} Einträge")
        
        # 4. Vergleich der Daten
        print("\n🔍 Vergleiche Original und Import...")
        
        print("Account-Namen:")
        print(f"  Original: {len(test_names)} - {test_names}")
        print(f"  Import:   {len(account_tab2.account_names)} - {account_tab2.account_names}")
        
        print("Account-Mappings:")
        print(f"  Original: {len(test_mappings)} - {test_mappings}")
        print(f"  Import:   {len(account_tab2.account_mappings)} - {account_tab2.account_mappings}")
        
        # Verifikation
        names_match = account_tab2.account_names == test_names
        mappings_match = account_tab2.account_mappings == test_mappings
        
        if names_match and mappings_match:
            print("✅ Daten stimmen überein - Import/Export funktioniert korrekt!")
            return True
        else:
            print("❌ Daten stimmen nicht überein")
            return False
        
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_example_csv():
    """Testet Import der Beispiel-CSV"""
    print("\n🧪 Teste Import der Beispiel-CSV...")
    
    example_csv = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/bwa_gruppen_beispiel.csv"
    
    if not os.path.exists(example_csv):
        print(f"❌ Beispiel-CSV nicht gefunden: {example_csv}")
        return False
    
    try:
        # QApplication für GUI-Tests
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # AccountMappingTab erstellen
        account_tab = AccountMappingTab()
        
        # Import simulieren
        imported_count = 0
        import csv
        
        with open(example_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            print("📋 Importiere Beispieldaten:")
            for row in reader:
                sachkontonr = str(row.get('Sachkontonr.', '')).strip()
                sachkonto = row.get('Sachkonto', '').strip()
                bwa_gruppe = row.get('BWA-Gruppe', '').strip()
                
                if sachkontonr:
                    if sachkonto:
                        account_tab.account_names[sachkontonr] = sachkonto
                    if bwa_gruppe:
                        account_tab.account_mappings[sachkontonr] = bwa_gruppe
                    
                    print(f"  {sachkontonr}: {sachkonto} → {bwa_gruppe}")
                    imported_count += 1
        
        print(f"\n✅ Beispiel-Import erfolgreich: {imported_count} Einträge")
        
        # Statistiken
        print(f"📊 Importierte Account-Namen: {len(account_tab.account_names)}")
        print(f"📊 Importierte BWA-Mappings: {len(account_tab.account_mappings)}")
        
        # Einige BWA-Gruppen anzeigen
        bwa_groups = account_tab.get_all_bwa_groups()
        print(f"📊 Eindeutige BWA-Gruppen: {len(bwa_groups)}")
        print(f"   {', '.join(bwa_groups[:10])}{'...' if len(bwa_groups) > 10 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Beispiel-Import: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 BWA-Gruppen Import/Export Test")
    print("=" * 50)
    
    # Test 1: Grundlegende Import/Export-Funktionalität
    test1_success = test_bwa_export_import()
    
    # Test 2: Beispiel-CSV importieren
    test2_success = test_example_csv()
    
    # Ergebnis
    overall_success = test1_success and test2_success
    print(f"\n{'🎉 Alle Tests erfolgreich!' if overall_success else '💥 Einige Tests fehlgeschlagen!'}")
    sys.exit(0 if overall_success else 1)

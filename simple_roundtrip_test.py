#!/usr/bin/env python3
"""
Vereinfachter JSON Roundtrip Test - umgeht GUI-Probleme
"""

import os
import sys
import tempfile
import json
from PySide6.QtCore import QSettings

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.csv_processor import CSVProcessor

def create_minimal_account_mappings():
    """Erstellt minimale Account-Mappings in QSettings"""
    settings = QSettings()
    
    # Standard-Mappings für die Test-CSV
    mappings = {
        "S03220": "Spenden",
        "S03223": "Spenden Wildvogelhilfe", 
        "S03215": "Einnahmen Verein",
        "S03216": "Mitgliedsbeiträge",
        "S02660": "Miete und Nebenkosten",
        "S02720": "Projektausgaben",
        "S02702": "Telefon/IT",
        "S02701": "Büromaterial/Porto",
        "S02703": "Reisekosten",
        "S02705": "Veranstaltungskosten",
        "S02710": "Jugendarbeit",
        "S02711": "Verwaltungskosten",
        "S02712": "Ehrenamtspauschale",
        "S02802": "Geschenke/Ehrungen",
        "S02811": "Werbekosten",
        "S04712": "Bankgebühren"
    }
    
    # Als JSON in QSettings speichern
    settings.setValue("account_mappings", json.dumps(mappings))
    
    print(f"✅ {len(mappings)} Account-Mappings in QSettings gespeichert")
    return mappings

def simple_roundtrip_test():
    """Vereinfachter Test für JSON Roundtrip"""
    print("🔄 Vereinfachter JSON Roundtrip Test...")
    
    # 1. Basis-Setup
    create_minimal_account_mappings()
    
    # 2. CSV Processor testen  
    print("📊 Teste CSV-Verarbeitung...")
    
    csv_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/test_anonymous.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Test-CSV nicht gefunden: {csv_path}")
        return False
    
    processor = CSVProcessor()
    success = processor.load_file(csv_path)
    
    if not success:
        print("❌ CSV konnte nicht geladen werden")
        return False
    
    print(f"✅ CSV geladen: {len(processor.processed_data)} Einträge")
    
    # 3. JSON-Export simulieren (richtige Struktur erstellen)
    print("📄 Erstelle JSON-Export-Struktur...")
    
    # Transaktionen nach Sachkonto gruppieren
    accounts_data = {}
    
    for _, row in processor.processed_data.iterrows():
        account_nr = row.get('Sachkontonr.', '')
        account_name = row.get('Sachkonto', '')
        
        if account_nr not in accounts_data:
            accounts_data[account_nr] = {
                'account_number': account_nr,
                'account_name': account_name,
                'transactions': []
            }
        
        transaction = {
            'booking_number': row.get('Buchungsnr.', ''),
            'date': row.get('Buchungstag', ''),
            'purpose': row.get('Verwendungszweck', ''),
            'amount': row.get('Betrag', ''),
            'amount_clean': row.get('Betrag_Clean', 0.0),
            'quarter': row.get('Quartal', 1)
        }
        
        accounts_data[account_nr]['transactions'].append(transaction)
    
    test_json_data = {
        "metadata": {
            "created_at": "2024-08-12T12:00:00",
            "version": "1.0",
            "source_file": "test_anonymous.csv"
        },
        "organization": {
            "name": "Test Organisation e.V.",
            "street": "Teststraße 123",
            "zip": "12345",
            "city": "Teststadt",
            "phone": "0123 456789",
            "email": "test@example.org",
            "info": "Test für JSON Roundtrip"
        },
        "balance_info": {
            "opening_balance": 1000.0,
            "period": "2024"
        },
        "account_mappings": {
            "S03220": "Spenden Allgemein",
            "S03223": "Spenden Projekte", 
            "S03215": "Vereinseinnahmen",
            "S03216": "Mitgliedsbeiträge",
            "S02660": "Miete und Nebenkosten",
            "S02720": "Projektausgaben",
            "S02702": "IT und Kommunikation",
            "S02701": "Büromaterial",
            "S02703": "Reisekosten",
            "S02705": "Veranstaltungen",
            "S02710": "Jugendarbeit",
            "S02711": "Verwaltung",
            "S02712": "Ehrenamt",
            "S02802": "Geschenke",
            "S02811": "Werbung",
            "S04712": "Bankgebühren"
        },
        "super_group_mappings": {
            "Spenden Allgemein": "Einnahmen",
            "Spenden Projekte": "Einnahmen",
            "Vereinseinnahmen": "Einnahmen", 
            "Mitgliedsbeiträge": "Einnahmen",
            "Miete und Nebenkosten": "Ausgaben",
            "Projektausgaben": "Ausgaben",
            "IT und Kommunikation": "Ausgaben",
            "Büromaterial": "Ausgaben",
            "Reisekosten": "Ausgaben",
            "Veranstaltungen": "Ausgaben",
            "Jugendarbeit": "Ausgaben",
            "Verwaltung": "Ausgaben",
            "Ehrenamt": "Ausgaben",
            "Geschenke": "Ausgaben",
            "Werbung": "Ausgaben",
            "Bankgebühren": "Ausgaben"
        },
        "account_details": list(accounts_data.values())
    }
    
    # JSON-Datei erstellen
    json_path = "/tmp/test_export.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(test_json_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Test-JSON erstellt: {json_path}")
    print(f"📊 JSON-Größe: {os.path.getsize(json_path)} Bytes")
    
    # 4. JSON wieder importieren
    print("📥 Teste JSON-Import...")
    
    processor2 = CSVProcessor()
    success2 = processor2.load_file(json_path)
    
    if not success2:
        print("❌ JSON konnte nicht importiert werden")
        return False
    
    print(f"✅ JSON importiert: {len(processor2.processed_data)} Einträge")
    
    # 5. Daten vergleichen
    print("🔍 Vergleiche Daten...")
    
    original_count = len(processor.processed_data)
    imported_count = len(processor2.processed_data)
    
    print(f"Original: {original_count} Einträge")
    print(f"Importiert: {imported_count} Einträge")
    
    if original_count == imported_count:
        print("✅ Anzahl Einträge stimmt überein")
        
        # Beträge vergleichen (falls vorhanden)
        if 'Betrag_Clean' in processor.processed_data.columns and 'Betrag_Clean' in processor2.processed_data.columns:
            original_sum = processor.processed_data['Betrag_Clean'].sum()
            imported_sum = processor2.processed_data['Betrag_Clean'].sum()
            
            print(f"Original Summe: {original_sum:.2f} €")
            print(f"Importiert Summe: {imported_sum:.2f} €")
            
            if abs(original_sum - imported_sum) < 0.01:
                print("✅ Beträge stimmen überein")
                print("🎉 JSON Roundtrip-Test erfolgreich!")
                return True
            else:
                print("❌ Beträge unterscheiden sich")
        else:
            print("✅ Struktureller Test erfolgreich (keine Beträge zu vergleichen)")
            return True
    else:
        print("❌ Anzahl Einträge unterscheidet sich")
    
    return False

if __name__ == "__main__":
    success = simple_roundtrip_test()
    print(f"\n{'✅ Test erfolgreich' if success else '❌ Test fehlgeschlagen'}")
    sys.exit(0 if success else 1)

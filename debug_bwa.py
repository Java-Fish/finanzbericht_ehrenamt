#!/usr/bin/env python3
"""
Debug-Script für BWA-Generator
"""

import os
import sys
import traceback
from PySide6.QtCore import QSettings

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.csv_processor import CSVProcessor
from utils.bwa_generator import BWAPDFGenerator

def debug_bwa_generation():
    """Debug der BWA-Generierung"""
    print("🔍 Debug BWA-Generierung...")
    
    # CSV-Datei laden
    csv_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/Finanzübersicht_2024.csv"
    
    processor = CSVProcessor()
    
    print(f"📊 Lade CSV: {csv_path}")
    success = processor.load_file(csv_path)
    
    if not success:
        print("❌ CSV konnte nicht geladen werden")
        return False
        
    print(f"✅ CSV geladen: {len(processor.processed_data)} Einträge")
    print(f"Datentyp processed_data: {type(processor.processed_data)}")
    
    if processor.processed_data is not None:
        print(f"Spalten: {list(processor.processed_data.columns)}")
        print(f"Erste 3 Zeilen:")
        print(processor.processed_data.head(3))
    
    # Einstellungen prüfen und setzen
    settings = QSettings()
    print(f"\n⚙️ Setze minimale Einstellungen...")
    
    # Organisationsdaten setzen
    settings.setValue("organization/name", "Test Organisation")
    settings.setValue("organization/street", "Teststraße 1")
    settings.setValue("organization/zip", "12345")
    settings.setValue("organization/city", "Teststadt")
    
    print(f"Organization: {settings.value('organization/name', 'Nicht gesetzt')}")
    print(f"Opening Balance: {settings.value('opening_balance', 'Nicht gesetzt')}")
    
    # PDF-Generator testen
    print(f"\n📄 Teste PDF-Generierung...")
    
    try:
        pdf_generator = BWAPDFGenerator()
        test_pdf_path = "/tmp/debug_test.pdf"
        
        # JSON-Export aktivieren
        settings.setValue("json_export", True)
        
        print("🔧 Rufe generate_bwa_pdf auf...")
        result = pdf_generator.generate_bwa_pdf(test_pdf_path, processor)
        
        if result:
            print(f"✅ PDF erfolgreich erstellt: {test_pdf_path}")
            if os.path.exists(test_pdf_path):
                print(f"📊 PDF-Größe: {os.path.getsize(test_pdf_path)} Bytes")
            
            # JSON prüfen
            json_path = test_pdf_path.replace('.pdf', '.json')
            if os.path.exists(json_path):
                print(f"✅ JSON erstellt: {json_path}")
                print(f"📊 JSON-Größe: {os.path.getsize(json_path)} Bytes")
            else:
                print(f"❌ JSON nicht gefunden: {json_path}")
        else:
            print("❌ PDF-Generierung fehlgeschlagen")
            
    except Exception as e:
        print(f"❌ Fehler bei PDF-Generierung: {e}")
        print("Traceback:")
        traceback.print_exc()
        
        # Debug: Versuche herauszufinden welches Objekt None ist
        print("\n🔍 Debug-Informationen:")
        try:
            # Test der kritischen Pfade
            print(f"processor.is_json_source: {getattr(processor, 'is_json_source', 'Nicht gesetzt')}")
            print(f"processor.processed_data type: {type(processor.processed_data)}")
            
            # Account Mappings testen
            print("🔧 Teste Kontenzuordnungen...")
            from src.settings.account_mapping import AccountMapping
            account_mapping = AccountMapping()
            mappings = account_mapping.get_account_mappings()
            print(f"Account mappings: {type(mappings)}, Anzahl: {len(mappings) if mappings else 0}")
            
        except Exception as debug_e:
            print(f"Debug-Fehler: {debug_e}")
        
        return False
        
    return True

if __name__ == "__main__":
    debug_bwa_generation()

#!/usr/bin/env python3
"""
Test für PDF-Generierung mit JSON-Mappings
"""

import os
import sys
import tempfile
from PySide6.QtCore import QSettings

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.csv_processor import CSVProcessor
from utils.bwa_generator import BWAPDFGenerator

def test_pdf_with_json_mappings():
    """Teste PDF-Generierung mit JSON-Mappings"""
    print("📄 Teste PDF-Generierung mit JSON-Mappings...")
    
    # Setup minimaler Einstellungen
    settings = QSettings()
    settings.setValue("organization/name", "Test Organisation e.V.")
    settings.setValue("organization/street", "Teststraße 123")
    settings.setValue("organization/zip", "12345")
    settings.setValue("organization/city", "Teststadt")
    settings.setValue("opening_balance", 1000.0)
    
    # JSON-Datei aus dem vorherigen Test verwenden
    json_path = "/tmp/test_export.json"
    
    if not os.path.exists(json_path):
        print(f"❌ JSON-Datei nicht gefunden: {json_path}")
        return False
    
    # 1. JSON laden
    print("📥 Lade JSON...")
    processor = CSVProcessor()
    success = processor.load_file(json_path)
    
    if not success:
        print("❌ JSON konnte nicht geladen werden")
        return False
    
    print(f"✅ JSON geladen: {len(processor.processed_data)} Einträge")
    print(f"JSON-Quelle: {processor.is_json_source}")
    
    # 2. Mappings prüfen
    print("\n🔍 Prüfe Mappings...")
    
    account_mappings = processor.get_json_account_mappings()
    super_group_mappings = processor.get_json_super_group_mappings()
    
    print(f"Account-Mappings: {len(account_mappings) if account_mappings else 0}")
    print(f"Super-Group-Mappings: {len(super_group_mappings) if super_group_mappings else 0}")
    
    # 3. PDF-Generierung versuchen
    print("\n📄 Versuche PDF-Generierung...")
    
    try:
        generator = BWAPDFGenerator()
        pdf_path = "/tmp/test_with_mappings.pdf"
        
        result = generator.generate_bwa_pdf(pdf_path, processor)
        
        if result:
            print(f"✅ PDF erfolgreich erstellt: {pdf_path}")
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                print(f"📊 PDF-Größe: {size} Bytes")
                
                if size > 1000:  # PDF sollte mehr als 1KB haben
                    print("✅ PDF hat vernünftige Größe - wahrscheinlich erfolgreich")
                    return True
                else:
                    print("⚠️ PDF sehr klein - möglicherweise leerer Inhalt")
                    return False
            else:
                print("❌ PDF-Datei wurde nicht erstellt")
                return False
        else:
            print("❌ PDF-Generierung fehlgeschlagen")
            return False
            
    except Exception as e:
        print(f"❌ Fehler bei PDF-Generierung: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_with_json_mappings()
    print(f"\n{'✅ PDF-Test erfolgreich' if success else '❌ PDF-Test fehlgeschlagen'}")
    sys.exit(0 if success else 1)

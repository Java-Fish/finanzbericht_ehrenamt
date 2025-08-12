#!/usr/bin/env python3
"""
Test-Script für JSON Roundtrip-Funktionalität
Testet den kompletten Workflow: CSV Import → PDF/JSON Export → JSON Import → PDF Export
"""

import os
import sys
import shutil
import tempfile
import pandas as pd
from pathlib import Path
from PySide6.QtCore import QSettings

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.csv_processor import CSVProcessor
from utils.bwa_generator import BWAPDFGenerator
from utils.file_handler import FileHandler

def compare_pdfs_roughly(pdf1_path, pdf2_path):
    """Vergleicht zwei PDFs grob anhand der Dateigröße"""
    try:
        size1 = os.path.getsize(pdf1_path)
        size2 = os.path.getsize(pdf2_path)
        
        # PDFs sollten ähnliche Größe haben (±20% Toleranz)
        size_diff = abs(size1 - size2) / max(size1, size2)
        return size_diff < 0.2
    except Exception as e:
        print(f"❌ Fehler beim PDF-Vergleich: {e}")
        return False

def test_json_roundtrip():
    """Test des kompletten JSON Roundtrip-Workflows"""
    print("🔄 Starte JSON Roundtrip-Test...")
    
    # Temporäres Verzeichnis für Tests
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Arbeitsverzeichnis: {temp_dir}")
        
        # 1. CSV-Datei laden
        csv_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/Finanzübersicht_2024.csv"
        if not os.path.exists(csv_path):
            print(f"❌ CSV-Datei nicht gefunden: {csv_path}")
            return False
            
        print(f"📊 Lade CSV: {csv_path}")
        
        # CSV Processor initialisieren
        processor = CSVProcessor()
        
        try:
            # CSV laden
            success = processor.load_file(csv_path)
            if not success:
                print("❌ CSV konnte nicht geladen werden")
                return False
                
            print(f"✅ CSV geladen: {len(processor.processed_data)} Einträge")
            
            # 2. Erstes PDF und JSON erstellen
            print("📄 Erstelle erstes PDF und JSON...")
            
            # JSON-Export in den Einstellungen aktivieren
            settings = QSettings()
            settings.setValue("json_export", True)
            
            pdf_generator = BWAPDFGenerator()
            
            # Erstes PDF erstellen
            pdf1_path = os.path.join(temp_dir, "original.pdf")
            json1_path = os.path.join(temp_dir, "export.json")
            
            # PDF generieren (JSON wird automatisch exportiert wenn aktiviert)
            pdf_success = pdf_generator.generate_bwa_pdf(pdf1_path, processor)
            
            if not pdf_success:
                print("❌ Erstes PDF konnte nicht erstellt werden")
                return False
                
            print(f"✅ Erstes PDF erstellt: {pdf1_path}")
            
            # JSON-Pfad sollte automatisch generiert worden sein (PDF-Name + .json)
            expected_json_path = pdf1_path.replace('.pdf', '.json')
            if os.path.exists(expected_json_path):
                json1_path = expected_json_path
                print(f"✅ JSON Export gefunden: {json1_path}")
            else:
                print(f"❌ JSON-Datei wurde nicht erstellt an erwartetem Pfad: {expected_json_path}")
                return False
                
            # 3. JSON wieder importieren
            print("📥 Importiere JSON...")
            
            processor2 = CSVProcessor()
            json_success = processor2.load_file(json1_path)
            
            if not json_success:
                print("❌ JSON konnte nicht importiert werden")
                return False
                
            print(f"✅ JSON importiert: {len(processor2.processed_data)} Einträge")
            
            # 4. Zweites PDF aus JSON-Daten erstellen
            print("📄 Erstelle zweites PDF aus JSON-Daten...")
            
            pdf2_path = os.path.join(temp_dir, "from_json.pdf")
            
            # PDF aus JSON-Daten generieren
            pdf_generator2 = BWAPDFGenerator()
            pdf2_success = pdf_generator2.generate_bwa_pdf(pdf2_path, processor2)
            
            if not pdf2_success:
                print("❌ Zweites PDF konnte nicht erstellt werden")
                return False
                
            print(f"✅ Zweites PDF erstellt: {pdf2_path}")
            
            # 5. PDFs vergleichen
            print("🔍 Vergleiche PDFs...")
            
            if not os.path.exists(pdf1_path) or not os.path.exists(pdf2_path):
                print("❌ Eine der PDF-Dateien existiert nicht")
                return False
                
            pdf_similar = compare_pdfs_roughly(pdf1_path, pdf2_path)
            
            print(f"📊 PDF 1 Größe: {os.path.getsize(pdf1_path)} Bytes")
            print(f"📊 PDF 2 Größe: {os.path.getsize(pdf2_path)} Bytes")
            
            if pdf_similar:
                print("✅ PDFs haben ähnliche Größe - Test erfolgreich!")
                return True
            else:
                print("❌ PDFs unterscheiden sich stark - möglicherweise Problem beim JSON-Import")
                return False
                
        except Exception as e:
            print(f"❌ Fehler im Test: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_json_roundtrip()
    if success:
        print("\n🎉 JSON Roundtrip-Test erfolgreich!")
        sys.exit(0)
    else:
        print("\n💥 JSON Roundtrip-Test fehlgeschlagen!")
        sys.exit(1)
